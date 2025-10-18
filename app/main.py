from fastapi import FastAPI, Depends, HTTPException, Response
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
    base_price: float
    stock_level: int
    category_name: str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float
    vat_rate: Optional[float] = 0.23
    category_id: int
    stock_level: int
    is_active: Optional[bool] = True

class ProductUpdate(ProductCreate):
    pass

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
        SELECT p.product_id, p.name, p.description, p.base_price, p.stock_level, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {"skip": skip, "limit": limit})
    products = result.fetchall()
    
    return [
        Product(
            product_id=p.product_id,
            name=p.name,
            description=p.description,
            base_price=float(p.base_price),
            stock_level=p.stock_level,
            category_name=p.category_name or "Uncategorized"
        )
        for p in products
    ]

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT p.product_id, p.name, p.description, p.base_price, p.stock_level, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
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
        base_price=float(product.base_price),
        stock_level=product.stock_level,
        category_name=product.category_name or "Uncategorized"
    )

@app.post("/products", response_model=Product, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    insert_query = text("""
        INSERT INTO products (name, description, base_price, vat_rate, category_id, stock_level, is_active)
        VALUES (:name, :description, :base_price, :vat_rate, :category_id, :stock_level, :is_active)
        RETURNING product_id
    """)

    result = db.execute(insert_query, {
        "name": product.name,
        "description": product.description,
        "base_price": product.base_price,
        "vat_rate": product.vat_rate,
        "category_id": product.category_id,
        "stock_level": product.stock_level,
        "is_active": product.is_active,
    })
    new_product_id = result.scalar()
    db.commit()

    return await get_product(new_product_id, db)

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    update_query = text("""
        UPDATE products
        SET name = :name,
            description = :description,
            base_price = :base_price,
            vat_rate = :vat_rate,
            category_id = :category_id,
            stock_level = :stock_level,
            is_active = :is_active,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = :product_id
    """)

    result = db.execute(update_query, {
        "name": product.name,
        "description": product.description,
        "base_price": product.base_price,
        "vat_rate": product.vat_rate,
        "category_id": product.category_id,
        "stock_level": product.stock_level,
        "is_active": product.is_active,
        "product_id": product_id,
    })

    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="Product not found")

    db.commit()
    return await get_product(product_id, db)

@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    delete_query = text("""
        DELETE FROM products
        WHERE product_id = :product_id
        RETURNING product_id
    """)

    result = db.execute(delete_query, {"product_id": product_id})
    deleted = result.fetchone()

    if not deleted:
        db.rollback()
        raise HTTPException(status_code=404, detail="Product not found")

    db.commit()
    return Response(status_code=204)

# Orders endpoints
@app.get("/orders", response_model=List[Order])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = text("""
        SELECT o.order_id, u.email as customer_email, o.total_amount, o.status as order_status, o.created_at::text as created_at
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
        SELECT o.order_id, u.email as customer_email, o.total_amount, o.status as order_status, o.created_at::text as created_at
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
        "order_items", "ratings_and_reviews", "discount_coupons", "carts"
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
