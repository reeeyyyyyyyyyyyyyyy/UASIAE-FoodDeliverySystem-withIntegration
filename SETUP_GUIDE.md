# Setup & Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- Python 3.9+ (untuk development)
- Git

## Quick Start

### 1. Clone Repository
```bash
cd /Users/rayyyhann/Documents/bismillah\ UAS
```

### 2. Build & Start Services
```bash
# Build images dan start containers
docker-compose up --build

# Atau untuk development dengan logs
docker-compose up -d
docker-compose logs -f
```

### 3. Verify Services
```bash
# Check status
docker-compose ps

# Expected output:
# NAME                  STATUS
# api-gateway           Up (healthy)
# user-service          Up (healthy)
# restaurant-service    Up (healthy)
# order-service         Up (healthy)
# payment-service       Up (healthy)
# driver-service        Up (healthy)
# user_db               Up (healthy)
# restaurant_db         Up (healthy)
# order_db              Up (healthy)
# payment_db            Up (healthy)
# driver_db             Up (healthy)
```

### 4. Access Services
```
API Gateway:       http://localhost:4000
User Service:      http://localhost:4001
Restaurant Service: http://localhost:4002
Order Service:     http://localhost:4003
Payment Service:   http://localhost:4004
Driver Service:    http://localhost:4005
```

### 5. Test Services
```bash
# Run test script
chmod +x test-services.sh
./test-services.sh

# Or manually test
curl http://localhost:4001/
curl http://localhost:4002/restaurants
curl http://localhost:4003/orders?user_id=5
```

---

## Database Access

### Direct MySQL Access

```bash
# User Service Database
mysql -h127.0.0.1 -P3307 -uroot -proot user_service_db

# Restaurant Service Database
mysql -h127.0.0.1 -P3312 -uroot -proot restaurant_service_db

# Order Service Database
mysql -h127.0.0.1 -P3309 -uroot -proot order_service_db

# Payment Service Database
mysql -h127.0.0.1 -P3310 -uroot -proot payment_service_db

# Driver Service Database
mysql -h127.0.0.1 -P3311 -uroot -proot driver_service_db
```

### Via Docker Container
```bash
# List all tables in user database
docker exec user_db mysql -uroot -proot -e "USE user_service_db; SHOW TABLES;"

# Run query
docker exec user_db mysql -uroot -proot -e "USE user_service_db; SELECT * FROM users;"

# Interactive shell
docker exec -it user_db mysql -uroot -proot user_service_db
```

---

## Common Commands

### Container Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (cleanup database)
docker-compose down -v

# Restart specific service
docker-compose restart user-service

# View logs
docker-compose logs user-service
docker-compose logs -f user-service  # Follow logs

# Execute command in container
docker-compose exec user-service bash
docker-compose exec user_db mysql -uroot -proot
```

### Database Backup/Restore
```bash
# Backup specific database
docker exec user_db mysqldump -uroot -proot user_service_db > user_service_backup.sql

# Backup all databases
for db in user_service_db restaurant_service_db order_service_db payment_service_db driver_service_db; do
  docker exec ${db%_service_db}_db mysqldump -uroot -proot $db > ${db}_backup.sql
done

# Restore database
docker exec -i user_db mysql -uroot -proot user_service_db < user_service_backup.sql
```

---

## Troubleshooting

### Service tidak bisa terkoneksi ke database

**Problem**: Connection refused atau timeout

**Solutions**:
```bash
# 1. Check jika database sudah healthy
docker-compose ps | grep _db

# 2. Check database logs
docker logs user_db | tail -20

# 3. Check network connectivity
docker network inspect iae-network

# 4. Verify environment variables
docker-compose exec user-service env | grep DATABASE

# 5. Restart database services
docker-compose down
docker-compose up --build -d
```

### Port sudah digunakan

**Problem**: `Bind for 0.0.0.0:4001 failed: port is already allocated`

**Solutions**:
```bash
# 1. Find process using port
lsof -i :4001

# 2. Kill process (if safe)
kill -9 <PID>

# 3. Or change port di docker-compose.yml
# Ubah "4001:8000" menjadi "4011:8000"
```

### Database tidak ter-initialize

**Problem**: Tables tidak ada saat service startup

**Solutions**:
```bash
# 1. Check jika SQL file ada
ls -la *.sql

# 2. Verify initialization script
docker logs user_db | grep "init.sql"

# 3. Force re-initialization
docker-compose down -v
docker volume rm user_db_data
docker-compose up --build -d

# 4. Or manually run init script
docker exec user_db mysql -uroot -proot user_service_db < user_service_db.sql
```

### Memory/Resource issues

**Problem**: Services crash atau CPU/memory spike

**Solutions**:
```yaml
# Add resource limits di docker-compose.yml
services:
  user-service:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# macOS: Docker Desktop > Preferences > Resources
# Linux: Adjust in /etc/docker/daemon.json
```

---

## Development Workflow

### Local Development (Without Docker)

```bash
# 1. Install Python dependencies
cd user-service
pip install -r requirements.txt

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup local .env file
cat > .env << EOF
DATABASE_URL=mysql+pymysql://root:root@localhost:3307/user_service_db
SECRET_KEY=your-secret-key
EOF

# 5. Run service locally
uvicorn app.main:app --reload --port 8000
```

### Development with Docker

```bash
# 1. Start only databases
docker-compose up -d user_db restaurant_db order_db payment_db driver_db

# 2. Run service locally
cd user-service
python -m uvicorn app.main:app --reload --port 8000

# This allows hot-reload development while using Docker databases
```

---

## Production Deployment

### Pre-deployment Checklist

- [ ] Update `SECRET_KEY` di environment
- [ ] Change default MySQL password
- [ ] Set `ALGORITHM` di JWT configuration
- [ ] Configure external service URLs (DOSWALLET_API_URL, etc.)
- [ ] Setup proper logging & monitoring
- [ ] Configure backup strategy
- [ ] Test all endpoints thoroughly

### Production Docker-Compose

```bash
# 1. Use production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 2. Or set environment
export ENVIRONMENT=production
docker-compose up -d
```

### Health Monitoring

```bash
# Automated health check script
while true; do
  for service in 4001 4002 4003 4004 4005; do
    curl -f http://localhost:$service/ || echo "Service on port $service is DOWN"
  done
  sleep 60
done
```

---

## API Documentation

Setiap service memiliki GraphQL endpoint di `/graphql`:

```
User Service:       POST http://localhost:4001/graphql
Restaurant Service: POST http://localhost:4002/graphql
Order Service:      POST http://localhost:4003/graphql
Payment Service:    POST http://localhost:4004/graphql
Driver Service:     POST http://localhost:4005/graphql
```

### Example GraphQL Query

```graphql
query {
  restaurants {
    id
    name
    cuisineType
    menus {
      id
      name
      price
      isAvailable
    }
  }
}
```

### Example GraphQL Mutation

```graphql
mutation {
  createOrder(
    userId: 5
    restaurantId: 1
    addressId: 1
    items: [
      {menuId: 1, menuName: "Item 1", price: 25000, quantity: 2}
    ]
  ) {
    id
    status
    totalPrice
  }
}
```

---

## Performance Optimization

### Database Connection Pooling
✅ Sudah dikonfigurasi di database.py:
- pool_size=10
- max_overflow=20
- pool_recycle=3600
- pool_pre_ping=True

### Caching Strategy
Untuk production, tambahkan Redis:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Query Optimization
- Tambahkan database indexes untuk frequently queried columns
- Implement pagination untuk large result sets
- Use GraphQL field selection untuk reduce data transfer

---

## Support & Documentation

Untuk dokumentasi lengkap setiap service, lihat:
- [USER SERVICE DOCS](user-service/README.md)
- [RESTAURANT SERVICE DOCS](restaurant-service/README.md)
- [ORDER SERVICE DOCS](order-service/README.md)
- [PAYMENT SERVICE DOCS](payment-service/README.md)
- [DRIVER SERVICE DOCS](driver-service/README.md)
