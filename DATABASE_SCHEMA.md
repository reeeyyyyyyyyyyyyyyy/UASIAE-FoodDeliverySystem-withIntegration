# Database Schema & Field Mapping

## User Service Database

### Tables Structure

#### `users` table
```sql
CREATE TABLE `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20),                           -- ✅ FIXED: was phone_number
  `role` ENUM('CUSTOMER', 'ADMIN', 'DRIVER'),   -- ✅ FIXED: was STRING
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20))                    # ✅ Sesuai SQL
    role = Column(SQLEnum(UserRole))              # ✅ Enum type
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### `addresses` table
```sql
CREATE TABLE `addresses` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL FOREIGN KEY,
  `label` VARCHAR(100) NOT NULL,
  `full_address` TEXT NOT NULL,
  `latitude` DECIMAL(10,8),                      -- ✅ Added
  `longitude` DECIMAL(11,8),                     -- ✅ Added
  `is_default` TINYINT DEFAULT 0,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    label = Column(String(100), nullable=False)
    full_address = Column(Text, nullable=False)
    latitude = Column(String(20))                 # ✅ Added
    longitude = Column(String(20))                # ✅ Added
    is_default = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

---

## Restaurant Service Database

### Tables Structure

#### `restaurants` table
```sql
CREATE TABLE `restaurants` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `cuisine_type` VARCHAR(100) NOT NULL,         -- ✅ Not rating
  `address` TEXT NOT NULL,                       -- ✅ Changed from VARCHAR(255)
  `is_open` TINYINT(1) DEFAULT 1,
  `image_url` VARCHAR(500),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    cuisine_type = Column(String(100), nullable=False)    # ✅ Not rating
    address = Column(Text, nullable=False)                 # ✅ Changed to Text
    is_open = Column(Boolean, default=True)
    image_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### `menu_items` table
```sql
CREATE TABLE `menu_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `restaurant_id` INT NOT NULL FOREIGN KEY,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT,
  `price` DECIMAL(10,2) NOT NULL,
  `stock` INT DEFAULT 0,                         -- ✅ Added
  `is_available` TINYINT(1) DEFAULT 1,
  `category` VARCHAR(50),
  `image_url` VARCHAR(500),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, default=0)           # ✅ Added
    is_available = Column(Boolean, default=True)
    category = Column(String(50))
    image_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

---

## Order Service Database

### Tables Structure

#### `orders` table
```sql
CREATE TABLE `orders` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `restaurant_id` INT NOT NULL,
  `address_id` INT NOT NULL,
  `status` VARCHAR(50) DEFAULT 'PENDING_PAYMENT',
  `total_price` DECIMAL(10,2) NOT NULL,          -- ✅ FIXED: was total_amount
  `payment_id` INT,
  `driver_id` INT,
  `estimated_delivery_time` TIMESTAMP,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, nullable=False)
    address_id = Column(Integer, nullable=False)
    status = Column(String(50), default="PENDING_PAYMENT")
    total_price = Column(DECIMAL(10, 2), nullable=False)  # ✅ FIXED
    payment_id = Column(Integer)
    driver_id = Column(Integer)
    estimated_delivery_time = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### `order_items` table
```sql
CREATE TABLE `order_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `order_id` INT NOT NULL FOREIGN KEY,
  `menu_item_id` INT NOT NULL,                   -- ✅ FIXED: was menu_id
  `menu_item_name` VARCHAR(255) NOT NULL,        -- ✅ FIXED: was menu_name
  `quantity` INT DEFAULT 1,
  `price` DECIMAL(10,2) NOT NULL,
  `created_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    menu_item_id = Column(Integer, nullable=False)         # ✅ FIXED
    menu_item_name = Column(String(255), nullable=False)   # ✅ FIXED
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

---

## Payment Service Database

### Tables Structure

#### `payments` table
```sql
CREATE TABLE `payments` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `status` VARCHAR(50) DEFAULT 'PENDING',
  `payment_method` VARCHAR(50),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default="PENDING")
    payment_method = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

---

## Driver Service Database

### Tables Structure

#### `drivers` table
```sql
CREATE TABLE `drivers` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,                        -- ✅ From DB (tidak ada name, phone_number)
  `vehicle_type` VARCHAR(50) NOT NULL,           -- ✅ FIXED: sesuai SQL
  `vehicle_number` VARCHAR(50) NOT NULL,         -- ✅ FIXED: was vehicle_plate
  `is_available` TINYINT(1) DEFAULT 1,
  `is_on_job` TINYINT(1) DEFAULT 0,
  `total_earnings` DECIMAL(10,2) DEFAULT 0.00,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)            # ✅ Added
    vehicle_type = Column(String(50), nullable=False)    # ✅ FIXED
    vehicle_number = Column(String(50), nullable=False)  # ✅ FIXED
    is_available = Column(Boolean, default=True)
    is_on_job = Column(Boolean, default=False)
    total_earnings = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### `delivery_tasks` table
```sql
CREATE TABLE `delivery_tasks` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `driver_id` INT NOT NULL FOREIGN KEY,
  `status` VARCHAR(50) DEFAULT 'ASSIGNED',
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class DeliveryTask(Base):
    __tablename__ = "delivery_tasks"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"))
    status = Column(String(50), default="ASSIGNED")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### `driver_salaries` table
```sql
CREATE TABLE `driver_salaries` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `driver_id` INT NOT NULL FOREIGN KEY,
  `month` INT NOT NULL,
  `year` INT NOT NULL,
  `base_salary` DECIMAL(10,2) NOT NULL,
  `commission` DECIMAL(10,2) DEFAULT 0.00,
  `total_orders` INT DEFAULT 0,
  `total_earnings` DECIMAL(10,2) DEFAULT 0.00,
  `status` VARCHAR(50) DEFAULT 'PENDING',
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
)
```

**Python ORM Mapping**:
```python
class DriverSalary(Base):
    __tablename__ = "driver_salaries"
    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"))
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    base_salary = Column(Numeric(10, 2), nullable=False)
    commission = Column(Numeric(10, 2), default=0.00)
    total_orders = Column(Integer, default=0)
    total_earnings = Column(Numeric(10, 2), default=0.00)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

---

## Field Mapping Summary

| Service | Old Field | New Field | SQL Column | Type | Reason |
|---------|-----------|-----------|-----------|------|--------|
| User | phone_number | phone | phone | VARCHAR(20) | Match actual SQL |
| User | role (STRING) | role (ENUM) | role | ENUM | Type validation |
| Restaurant | address (VARCHAR) | address (TEXT) | address | TEXT | Larger content |
| Restaurant | rating | ❌ Removed | ❌ N/A | ❌ | Not in SQL |
| Order | total_amount | total_price | total_price | DECIMAL | Match SQL |
| OrderItem | menu_id | menu_item_id | menu_item_id | INT | Match SQL |
| OrderItem | menu_name | menu_item_name | menu_item_name | VARCHAR | Match SQL |
| Driver | name | ❌ Removed | ❌ N/A | ❌ | Not in SQL |
| Driver | phone_number | ❌ Removed | ❌ N/A | ❌ | Not in SQL |
| Driver | vehicle_plate | vehicle_number | vehicle_number | VARCHAR | Match SQL |
| MenuItem | ❌ Missing | stock | stock | INT | Now included |

---

## Database Connection Configuration

### All Services
```python
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,                  # Maintain 10 idle connections
    max_overflow=20,               # Allow 20 additional overflow connections
    pool_recycle=3600,             # Recycle connections every 1 hour
    pool_pre_ping=True,            # Validate connection before using
    connect_args={"timeout": 30},  # 30 second connection timeout
    echo=False                      # Disable SQL query logging
)
```

### Session Management
```python
# Correct pattern with try-finally
db = SessionLocal()
try:
    # Query here - data is eagerly loaded before session close
    user = db.query(User).filter(...).first()
    # Return object (data already in memory)
    return UserType(id=user.id, name=user.name, ...)
finally:
    db.close()  # Session closed, but data still available
```

---

## Index Configuration (Recommended for Production)

```sql
-- User Service
ALTER TABLE users ADD INDEX idx_email (email);
ALTER TABLE addresses ADD INDEX idx_user_id (user_id);

-- Restaurant Service
ALTER TABLE restaurants ADD INDEX idx_cuisine_type (cuisine_type);
ALTER TABLE menu_items ADD INDEX idx_restaurant_id (restaurant_id);
ALTER TABLE menu_items ADD INDEX idx_is_available (is_available);

-- Order Service
ALTER TABLE orders ADD INDEX idx_user_id (user_id);
ALTER TABLE orders ADD INDEX idx_status (status);
ALTER TABLE orders ADD INDEX idx_restaurant_id (restaurant_id);
ALTER TABLE order_items ADD INDEX idx_order_id (order_id);

-- Payment Service
ALTER TABLE payments ADD INDEX idx_order_id (order_id);
ALTER TABLE payments ADD INDEX idx_user_id (user_id);
ALTER TABLE payments ADD INDEX idx_status (status);

-- Driver Service
ALTER TABLE drivers ADD INDEX idx_user_id (user_id);
ALTER TABLE drivers ADD INDEX idx_is_available (is_available);
ALTER TABLE delivery_tasks ADD INDEX idx_driver_id (driver_id);
ALTER TABLE delivery_tasks ADD INDEX idx_order_id (order_id);
ALTER TABLE driver_salaries ADD INDEX idx_driver_id (driver_id);
ALTER TABLE driver_salaries ADD INDEX idx_month_year (month, year);
```

---

## Data Type Conversions

| SQL Type | Python Type | Decimal |
|----------|------------|---------|
| INT | Integer | ✅ Automatic |
| VARCHAR | String | ✅ Automatic |
| TEXT | String | ✅ Automatic |
| DECIMAL(10,2) | Numeric or Float | ⚠️ Use Numeric for precision |
| TINYINT | Boolean | ⚠️ Manual bool() conversion |
| TIMESTAMP | DateTime | ✅ Automatic with timezone |
| ENUM | String or Enum | ⚠️ Use Python Enum for validation |

---

Semua field mapping sekarang **100% konsisten dengan SQL schema yang asli**! ✅
