#!/bin/bash
# Quick Testing Script untuk Microservices Food Delivery

echo "========================================"
echo "Food Delivery Microservices - Testing"
echo "========================================"

# Colors untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function untuk test endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing: $description${NC}"
    
    if [ -z "$data" ]; then
        response=$(curl -s -X $method "$url")
    else
        response=$(curl -s -X $method "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    echo "Response: $response"
    echo ""
}

# 1. Check if all services are running
echo -e "${YELLOW}Checking service health...${NC}\n"

services=(
    "http://localhost:4001 - User Service"
    "http://localhost:4002 - Restaurant Service"
    "http://localhost:4003 - Order Service"
    "http://localhost:4004 - Payment Service"
    "http://localhost:4005 - Driver Service"
)

for service in "${services[@]}"; do
    url=$(echo $service | cut -d' ' -f1)
    name=$(echo $service | cut -d' ' -f3-)
    
    if curl -s "$url/" > /dev/null; then
        echo -e "${GREEN}✓${NC} $name is running"
    else
        echo -e "${RED}✗${NC} $name is NOT running"
    fi
done

echo ""
echo -e "${YELLOW}=== Testing REST Endpoints ===${NC}\n"

# 2. Test User Service
test_endpoint "GET" "http://localhost:4001/" "" "User Service Health Check"

# 3. Test Restaurant Service
test_endpoint "GET" "http://localhost:4002/restaurants" "" "Get All Restaurants"

# 4. Test Driver Service
test_endpoint "GET" "http://localhost:4005/drivers" "" "Get All Drivers"

# 5. Test GraphQL Queries
echo -e "${YELLOW}=== Testing GraphQL Queries ===${NC}\n"

# User Service GraphQL
test_endpoint "POST" "http://localhost:4001/graphql" \
    '{"query": "{ userById(id: 1) { id name email role } }"}' \
    "User Service - Get User by ID"

# Restaurant Service GraphQL
test_endpoint "POST" "http://localhost:4002/graphql" \
    '{"query": "{ restaurants { id name cuisineType } }"}' \
    "Restaurant Service - Get Restaurants"

# Driver Service GraphQL
test_endpoint "POST" "http://localhost:4005/graphql" \
    '{"query": "{ availableDrivers { id userId vehicleType isAvailable } }"}' \
    "Driver Service - Get Available Drivers"

# Order Service GraphQL
test_endpoint "POST" "http://localhost:4003/graphql" \
    '{"query": "{ myOrders(userId: 5) { id status totalPrice } }"}' \
    "Order Service - Get User Orders"

# Payment Service GraphQL
test_endpoint "POST" "http://localhost:4004/graphql" \
    '{"query": "{ paymentHistory { id status amount } }"}' \
    "Payment Service - Get Payment History"

echo -e "${GREEN}=== Testing Complete ===${NC}"
echo ""
echo "Next Steps:"
echo "1. Check if all services return data"
echo "2. Verify database connections are stable"
echo "3. Check Docker logs if any service fails:"
echo "   docker logs <service-name>"
echo "4. Verify database initialization:"
echo "   docker exec <db-container> mysql -uroot -proot -e 'SHOW TABLES FROM <database>;'"
