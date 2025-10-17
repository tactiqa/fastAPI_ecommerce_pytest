# FastAPI E-Commerce API Documentation

## Overview

This FastAPI application provides a RESTful API for an e-commerce system connected to a Supabase PostgreSQL database.

**Base URL:** `http://localhost:8802`

---

## Database Information

- **Provider:** Supabase (PostgreSQL)
- **Total Records:** 1,000+ rows across multiple tables
- **Key Tables:** users (51), categories (48), products (96), orders (84), reviews (100)

---

## Available Endpoints

### 1. Health Check Endpoints

#### GET `/health`
Simple health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8802/health
```

---

#### GET `/`
Detailed health check with database connection status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Example:**
```bash
curl http://localhost:8802/
```

---

### 2. Database Statistics

#### GET `/stats`
Get row counts for all tables in the database.

**Response:**
```json
{
  "users": 51,
  "categories": 48,
  "products": 96,
  "orders": 84,
  "order_items": 286,
  "ratings_and_reviews": 0,
  "discount_coupons": 0,
  "carts": 17
}
```

**Example:**
```bash
curl http://localhost:8802/stats
```

---

### 3. Products Endpoints

#### GET `/products`
Get a list of all products with pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum number of records to return

**Response:**
```json
[
  {
    "product_id": 203,
    "name": "iPhone",
    "description": "Third care term analysis anyone...",
    "base_price": 836.90,
    "stock_level": 1,
    "category_name": "Smartphones"
  }
]
```

**Examples:**
```bash
# Get first 10 products
curl "http://localhost:8802/products?limit=10"

# Get products 20-30
curl "http://localhost:8802/products?skip=20&limit=10"

# Get all products (up to 100)
curl "http://localhost:8802/products"
```

---

#### GET `/products/{product_id}`
Get details of a specific product by ID.

**Path Parameters:**
- `product_id` (int) - The product ID

**Response:**
```json
{
  "product_id": 203,
  "name": "iPhone",
  "description": "Third care term analysis anyone...",
  "base_price": 836.90,
  "stock_level": 1,
  "category_name": "Smartphones"
}
```

**Error Response (404):**
```json
{
  "detail": "Product not found"
}
```

**Examples:**
```bash
# Get product with ID 203
curl http://localhost:8802/products/203

# Get product with ID 205
curl http://localhost:8802/products/205
```

---

### 4. Orders Endpoints

#### GET `/orders`
Get a list of all orders with pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum number of records to return

**Response:**
```json
[
  {
    "order_id": 70,
    "customer_email": "fmendoza@example.org",
    "total_amount": 2338.23,
    "order_status": "delivered",
    "created_at": "2025-10-17 00:08:28.28153+00"
  }
]
```

**Examples:**
```bash
# Get first 10 orders
curl "http://localhost:8802/orders?limit=10"

# Get orders 5-10
curl "http://localhost:8802/orders?skip=5&limit=5"
```

---

#### GET `/orders/{order_id}`
Get details of a specific order by ID.

**Path Parameters:**
- `order_id` (int) - The order ID

**Response:**
```json
{
  "order_id": 70,
  "customer_email": "fmendoza@example.org",
  "total_amount": 2338.23,
  "order_status": "delivered",
  "created_at": "2025-10-17 00:08:28.28153+00"
}
```

**Error Response (404):**
```json
{
  "detail": "Order not found"
}
```

**Examples:**
```bash
# Get order with ID 70
curl http://localhost:8802/orders/70
```

---

## Data Models

### Product
```typescript
{
  product_id: number,
  name: string,
  description: string | null,
  base_price: number,
  stock_level: number,
  category_name: string
}
```

### Order
```typescript
{
  order_id: number,
  customer_email: string,
  total_amount: number,
  order_status: string,
  created_at: string
}
```

---

## Testing the API

### Using the Test Script

Run the comprehensive test script:

```bash
./test_api.sh
```

### Using curl

```bash
# Test all endpoints
curl http://localhost:8802/health
curl http://localhost:8802/
curl http://localhost:8802/stats
curl http://localhost:8802/products?limit=5
curl http://localhost:8802/products/203
curl http://localhost:8802/orders?limit=3
curl http://localhost:8802/orders/70
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8802"

# Get products
response = requests.get(f"{BASE_URL}/products", params={"limit": 10})
products = response.json()
print(f"Found {len(products)} products")

# Get specific product
product_id = 203
response = requests.get(f"{BASE_URL}/products/{product_id}")
product = response.json()
print(f"Product: {product['name']} - ${product['base_price']}")

# Get orders
response = requests.get(f"{BASE_URL}/orders", params={"limit": 5})
orders = response.json()
print(f"Found {len(orders)} orders")
```

---

## Database Seeding

To reseed the database with fresh test data:

```bash
# Clear existing data and seed with new data
python3 database/scripts/seed_database.py --clear

# Seed without clearing (will fail if data exists)
python3 database/scripts/seed_database.py
```

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI:** http://localhost:8802/docs
- **ReDoc:** http://localhost:8802/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test endpoints directly in the browser
- Download OpenAPI specification

---

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `404` - Resource not found
- `500` - Internal server error
- `503` - Service unavailable (database connection failed)

Error responses include a `detail` field with the error message:

```json
{
  "detail": "Product not found"
}
```

---

## CORS Configuration

The API is configured to accept requests from any origin (`*`). This is suitable for development but should be restricted in production.

---

## Database Schema

The Supabase database uses the following schema:

**Products Table:**
- `product_id` (integer, primary key)
- `name` (varchar)
- `description` (text)
- `base_price` (numeric)
- `vat_rate` (numeric)
- `stock_level` (integer)
- `category_id` (integer, foreign key)
- `is_active` (boolean)
- `created_at` (timestamp)

**Orders Table:**
- `order_id` (integer, primary key)
- `user_id` (integer, foreign key)
- `total_amount` (numeric)
- `status` (varchar)
- `created_at` (timestamp)

---

## Environment Variables

Required environment variables (in `.env` file):

```env
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
```

---

## Running the API

### Using Docker

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker logs -f fastapi-ecommerce-api

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python app/main.py

# Or using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8802 --reload
```

---

## Next Steps

1. **Add Authentication:** Implement JWT-based authentication
2. **Add POST/PUT/DELETE:** Create endpoints for creating/updating/deleting resources
3. **Add Filtering:** Implement product filtering by category, price range, etc.
4. **Add Search:** Implement full-text search for products
5. **Add Cart Management:** Endpoints for managing shopping carts
6. **Add Order Creation:** Endpoint for creating new orders
7. **Add Reviews:** Endpoints for product reviews and ratings

---

## Support

For issues or questions, check:
- API logs: `docker logs fastapi-ecommerce-api`
- Database connection: `python3 database/scripts/check_db_direct.py`
- Schema verification: `python3 database/scripts/check_schema.py`
