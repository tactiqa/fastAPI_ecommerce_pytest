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
