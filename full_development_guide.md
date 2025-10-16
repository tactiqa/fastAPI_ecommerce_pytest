# FastAPI E-Commerce Backend - Complete Development Guide

This comprehensive guide provides everything needed to set up and run the FastAPI e-commerce backend using Docker, connected to your Supabase PostgreSQL database.

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **Supabase account** with PostgreSQL database
- **Git** for version control
- **Terminal/Command Prompt** access

## 🏗️ Project Structure

```
fastapi-ecommerce/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API endpoints
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── database/
│   ├── schemas/             # SQL schema files
│   ├── scripts/             # Database utilities
│   └── docs/                # Database documentation
├── docker-compose.yml       # Full stack deployment
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── .env.example           # Environment template
```

## 🚀 Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd fastapi-ecommerce

# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
nano .env  # or use your preferred editor
```

### 2. Environment Configuration

Create `.env` file in the project root with your Supabase credentials:

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
nano .env
```

Required variables:
```bash
# Supabase Database (get from Supabase Dashboard > Project Settings > Database)
SUPABASE_DATABASE_URL=postgresql://postgres.your-project-id:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres

# Supabase API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. Build and Run with Docker

```bash
# Option 1: Using Docker Compose (Recommended)
cd docker
docker-compose up -d

# Option 2: Using Docker directly
docker build -f docker/Dockerfile -t e-commerce-api .
docker run -d \
    -p 8802:8802 \
    --name e-commerce-instance \
    -e SUPABASE_DATABASE_URL="<YOUR_SUPABASE_CONNECTION_URL>" \
    e-commerce-api

# Option 3: From project root
docker build -f docker/Dockerfile -t e-commerce-api .
docker run -d -p 8802:8802 --name e-commerce-instance e-commerce-api
```

### 4. Access the API

- **API Documentation**: http://localhost:8802/docs
- **Health Check**: http://localhost:8802/
- **Database Stats**: http://localhost:8802/stats
- **pgAdmin** (if using docker-compose): http://localhost:8080

## 📊 Database Schema Overview

### Core Tables
- **users** - Customer and admin accounts
- **categories** - Product categories
- **products** - Product catalog
- **orders** - Customer orders
- **order_items** - Individual items in orders
- **reviews** - Product reviews and ratings
- **coupons** - Discount codes and promotions
- **shopping_cart** - Persistent cart functionality

### Pre-seeded Data
- **51 Users** (1 admin: admin@ecommerce.com / admin123)
- **101 Products** across 48 categories
- **68 Orders** with 232 line items
- **92 Reviews** with ratings
- **8 Active Coupons** (WELCOME10, SAVE20, etc.)

## 🔧 Requirements (requirements.txt)

```txt
# Database
psycopg2-binary==2.9.9
python-dotenv==1.0.0

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# HTTP Client
requests==2.31.0
httpx==0.26.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0

# Data Generation
faker==22.6.0
```

## 🐳 Docker Configuration

### Dockerfile

```dockerfile
# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8802

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY database/ ./database/

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Expose port
EXPOSE 8802

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8802/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8802"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  fastapi-ecommerce:
    build: .
    container_name: fastapi-ecommerce-api
    ports:
      - "8802:8802"
    environment:
      - SUPABASE_DATABASE_URL=${SUPABASE_DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    volumes:
      - ./app:/app/app
      - ./database:/app/database
    depends_on:
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8802/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: fastapi-ecommerce-db
    environment:
      - POSTGRES_USER=ecommerce_user
      - POSTGRES_PASSWORD=ecommerce_password
      - POSTGRES_DB=ecommerce_db
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schemas:/docker-entrypoint-initdb.d
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ecommerce_user -d ecommerce_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: fastapi-ecommerce-pgadmin
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@ecommerce.com
      - PGADMIN_DEFAULT_PASSWORD=admin123
    ports:
      - "8080:80"
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  default:
    name: ecommerce-network
```

## 🚀 Main Application Code (app/main.py)

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No database URL provided. Set SUPABASE_DATABASE_URL or DATABASE_URL environment variable.")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create FastAPI app
app = FastAPI(
    title="FastAPI E-Commerce Backend",
    description="Complete e-commerce backend with FastAPI and PostgreSQL",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    database: str
    timestamp: str

class Product(BaseModel):
    product_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    category_name: str

class Order(BaseModel):
    order_id: int
    customer_email: str
    total_amount: float
    order_status: str
    created_at: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return HealthCheck(
            status="healthy",
            database="connected",
            timestamp="2024-01-01T00:00:00Z"
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}

# Products endpoints
@app.get("/products", response_model=List[Product])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = text("""
        SELECT p.product_id, p.name, p.description, p.price, p.stock_quantity, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_id
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {"skip": skip, "limit": limit})
    products = result.fetchall()
    
    return [
        Product(
            product_id=p.product_id,
            name=p.name,
            description=p.description,
            price=float(p.price),
            stock_quantity=p.stock_quantity,
            category_name=p.category_name
        )
        for p in products
    ]

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT p.product_id, p.name, p.description, p.price, p.stock_quantity, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = :product_id
    """)
    result = db.execute(query, {"product_id": product_id})
    product = result.fetchone()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(
        product_id=product.product_id,
        name=product.name,
        description=product.description,
        price=float(product.price),
        stock_quantity=product.stock_quantity,
        category_name=product.category_name
    )

# Orders endpoints
@app.get("/orders", response_model=List[Order])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = text("""
        SELECT o.order_id, u.email as customer_email, o.total_amount, o.order_status, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        ORDER BY o.created_at DESC
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {"skip": skip, "limit": limit})
    orders = result.fetchall()
    
    return [
        Order(
            order_id=o.order_id,
            customer_email=o.customer_email,
            total_amount=float(o.total_amount),
            order_status=o.order_status,
            created_at=str(o.created_at)
        )
        for o in orders
    ]

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT o.order_id, u.email as customer_email, o.total_amount, o.order_status, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_id = :order_id
    """)
    result = db.execute(query, {"order_id": order_id})
    order = result.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return Order(
        order_id=order.order_id,
        customer_email=order.customer_email,
        total_amount=float(order.total_amount),
        order_status=order.order_status,
        created_at=str(order.created_at)
    )

# Database stats endpoint
@app.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    stats = {}
    
    tables = [
        "users", "categories", "products", "orders", 
        "order_items", "reviews", "coupons", "shopping_cart"
    ]
    
    for table in tables:
        try:
            query = text(f"SELECT COUNT(*) as count FROM {table}")
            result = db.execute(query)
            stats[table] = result.scalar()
        except Exception:
            stats[table] = 0
    
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8802)
```

## 🧪 Testing the API

### Quick Test Commands

```bash
# Test health endpoint
curl http://localhost:8802/

# Get all products
curl http://localhost:8802/products

# Get specific product
curl http://localhost:8802/products/1

# Get all orders
curl http://localhost:8802/orders

# Get database stats
curl http://localhost:8802/stats
```

### Admin Test Account
- **Email**: admin@ecommerce.com
- **Password**: admin123

### Customer Test Accounts
- All customers use password: `password123`
- Sample emails: samuelhoffman@example.com, santiagostephanie@example.org

## 🔧 Development Commands

### Docker Commands

```bash
# Build image
docker build -t e-commerce-api .

# Run container
docker run -d -p 8802:8802 --name e-commerce-instance -e SUPABASE_DATABASE_URL="<URL>" e-commerce-api

# View logs
docker logs e-commerce-instance

# Stop container
docker stop e-commerce-instance

# Remove container
docker rm e-commerce-instance

# Use docker-compose
docker-compose up -d
docker-compose down
docker-compose logs -f
```

### Database Commands

```bash
# Check database connection
python database/scripts/check_db_direct.py

# Reset database (recreate schema)
python database/scripts/migrate_to_serial.py --confirm

# Seed fresh data
python database/scripts/seed_database.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify your `SUPABASE_DATABASE_URL` is correct
   - Check if Supabase project is running
   - Ensure network connectivity

2. **Port Already in Use**
   - Change port mapping: `-p 8803:8802`
   - Kill existing process: `lsof -ti:8802 | xargs kill -9`

3. **Docker Build Fails**
   - Clear Docker cache: `docker system prune -a`
   - Check internet connection
   - Verify requirements.txt syntax

4. **Permission Denied**
   - Use `sudo` for Docker commands on Linux
   - Add user to docker group: `sudo usermod -aG docker $USER`

### Health Check Endpoints

- **GET** `/` - Full health check with database status
- **GET** `/health` - Simple health check
- **GET** `/stats` - Database statistics

## 📚 Next Steps

1. **Authentication**: Implement JWT-based authentication
2. **Product Management**: Add CRUD endpoints for products
3. **Order Processing**: Complete order lifecycle management
4. **Shopping Cart**: Implement cart functionality
5. **Payment Integration**: Add payment processing
6. **Email Notifications**: Order confirmations and updates
7. **Admin Dashboard**: Create admin endpoints
8. **Testing**: Add comprehensive test suite

## 🔗 Useful Links

- [Supabase Dashboard](https://supabase.com/dashboard)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Status**: ✅ Ready for development
**Last Updated**: October 16, 2025
**Next Milestone**: Implement authentication and user management
