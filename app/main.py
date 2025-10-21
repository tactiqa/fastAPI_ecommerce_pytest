from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
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

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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
    product_id: str
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
    category_id: str
    stock_level: int
    is_active: Optional[bool] = True

class ProductUpdate(ProductCreate):
    pass

class Order(BaseModel):
    order_id: str
    customer_email: str
    total_amount: float
    order_status: str
    created_at: str

class OrderItemDetail(BaseModel):
    order_item_id: str
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    unit_price: float

class OrderCreateRequest(BaseModel):
    user_id: str
    shipping_address_id: str

class OrderDetailResponse(Order):
    items: List[OrderItemDetail]

class CartItemCreate(BaseModel):
    user_id: str
    product_id: str
    quantity: int = Field(gt=0)
    variant_id: Optional[str] = None

class CartItemResponse(BaseModel):
    cart_item_id: str
    cart_id: str
    product_id: str
    quantity: int
    variant_id: Optional[str] = None
    product_name: str
    base_price: float

class CartResponse(BaseModel):
    cart_id: str
    user_id: str
    items: List[CartItemResponse]
    total_quantity: int

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
            product_id=str(p.product_id),
            name=p.name,
            description=p.description,
            base_price=float(p.base_price),
            stock_level=p.stock_level,
            category_name=p.category_name or "Uncategorized"
        )
        for p in products
    ]

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, db: Session = Depends(get_db)):
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
        product_id=str(product.product_id),
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
async def update_product(product_id: str, product: ProductUpdate, db: Session = Depends(get_db)):
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
async def delete_product(product_id: str, db: Session = Depends(get_db)):
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
            order_id=str(o.order_id),
            customer_email=o.customer_email,
            total_amount=float(o.total_amount),
            order_status=o.order_status,
            created_at=str(o.created_at)
        )
        for o in orders
    ]

@app.get("/users/{user_id}/orders", response_model=List[Order])
async def get_user_orders(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_result = db.execute(
        text("""
            SELECT user_id, email
            FROM users
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()

    if not user_result:
        raise HTTPException(status_code=404, detail="User not found")

    query = text("""
        SELECT o.order_id, :customer_email AS customer_email, o.total_amount, o.status as order_status, o.created_at::text as created_at
        FROM orders o
        WHERE o.user_id = :user_id
        ORDER BY o.created_at DESC
        LIMIT :limit OFFSET :skip
    """)

    result = db.execute(
        query,
        {
            "user_id": user_id,
            "customer_email": user_result.email,
            "skip": skip,
            "limit": limit,
        }
    )
    orders = result.fetchall()

    return [
        Order(
            order_id=str(o.order_id),
            customer_email=o.customer_email,
            total_amount=float(o.total_amount),
            order_status=o.order_status,
            created_at=str(o.created_at)
        )
        for o in orders
    ]

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, db: Session = Depends(get_db)):
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
        order_id=str(order.order_id),
        customer_email=order.customer_email,
        total_amount=float(order.total_amount),
        order_status=order.order_status,
        created_at=str(order.created_at)
    )

@app.post("/orders", response_model=OrderDetailResponse, status_code=201)
async def create_order(order_request: OrderCreateRequest, db: Session = Depends(get_db)):
    cart_row = db.execute(
        text(
            """
            SELECT cart_id
            FROM carts
            WHERE user_id = :user_id
            """
        ),
        {"user_id": order_request.user_id}
    ).fetchone()

    if not cart_row:
        raise HTTPException(status_code=400, detail="Cart not found for user")

    address_row = db.execute(
        text(
            """
            SELECT address_id
            FROM addresses
            WHERE address_id = :address_id AND user_id = :user_id
            """
        ),
        {"address_id": order_request.shipping_address_id, "user_id": order_request.user_id}
    ).fetchone()

    if not address_row:
        raise HTTPException(status_code=400, detail="Shipping address not found for user")

    items = db.execute(
        text(
            """
            SELECT ci.cart_item_id, ci.product_id, ci.variant_id, ci.quantity,
                   p.base_price, COALESCE(pv.additional_price, 0) AS additional_price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            LEFT JOIN product_variants pv ON ci.variant_id = pv.variant_id
            WHERE ci.cart_id = :cart_id
            ORDER BY ci.cart_item_id
            """
        ),
        {"cart_id": cart_row.cart_id}
    ).fetchall()

    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = Decimal("0")
    data_for_items = []

    for item in items:
        base_price = Decimal(item.base_price)
        additional_price = Decimal(item.additional_price)
        unit_price = base_price + additional_price
        line_total = unit_price * item.quantity
        total_amount += line_total
        data_for_items.append(
            {
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
            }
        )

    try:
        order_result = db.execute(
            text(
                """
                INSERT INTO orders (user_id, total_amount, shipping_address_id)
                VALUES (:user_id, :total_amount, :shipping_address_id)
                RETURNING order_id
                """
            ),
            {
                "user_id": order_request.user_id,
                "total_amount": float(total_amount),
                "shipping_address_id": order_request.shipping_address_id,
            }
        )
        order_id = order_result.scalar()

        for item_data in data_for_items:
            db.execute(
                text(
                    """
                    INSERT INTO order_items (order_id, product_id, variant_id, quantity, unit_price)
                    VALUES (:order_id, :product_id, :variant_id, :quantity, :unit_price)
                    """
                ),
                {
                    "order_id": order_id,
                    "product_id": item_data["product_id"],
                    "variant_id": item_data["variant_id"],
                    "quantity": item_data["quantity"],
                    "unit_price": float(item_data["unit_price"]),
                }
            )

        db.execute(
            text(
                """
                DELETE FROM cart_items
                WHERE cart_id = :cart_id
                """
            ),
            {"cart_id": cart_row.cart_id}
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    order_summary = await get_order(order_id, db)

    order_items = db.execute(
        text(
            """
            SELECT order_item_id, product_id, variant_id, quantity, unit_price
            FROM order_items
            WHERE order_id = :order_id
            ORDER BY order_item_id
            """
        ),
        {"order_id": order_id}
    ).fetchall()

    return OrderDetailResponse(
        order_id=order_summary.order_id,
        customer_email=order_summary.customer_email,
        total_amount=order_summary.total_amount,
        order_status=order_summary.order_status,
        created_at=order_summary.created_at,
        items=[
            OrderItemDetail(
                order_item_id=str(item.order_item_id),
                product_id=str(item.product_id),
                variant_id=str(item.variant_id) if item.variant_id else None,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
            )
            for item in order_items
        ],
    )

@app.get("/cart/{user_id}", response_model=CartResponse)
async def get_cart(user_id: str, db: Session = Depends(get_db)):
    cart_result = db.execute(
        text("""
            SELECT cart_id
            FROM carts
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()

    if cart_result:
        cart_id = cart_result.cart_id
    else:
        new_cart = db.execute(
            text("""
                INSERT INTO carts (user_id)
                VALUES (:user_id)
                RETURNING cart_id
            """),
            {"user_id": user_id}
        )
        cart_id = new_cart.scalar()
        db.commit()

    items = db.execute(
        text("""
            SELECT ci.cart_item_id, ci.cart_id, ci.product_id, ci.quantity, ci.variant_id,
                   p.name AS product_name, p.base_price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.cart_id = :cart_id
            ORDER BY ci.cart_item_id
        """),
        {"cart_id": cart_id}
    ).fetchall()

    response_items = [
        CartItemResponse(
            cart_item_id=str(item.cart_item_id),
            cart_id=str(item.cart_id),
            product_id=str(item.product_id),
            quantity=item.quantity,
            variant_id=str(item.variant_id) if item.variant_id else None,
            product_name=item.product_name,
            base_price=float(item.base_price)
        )
        for item in items
    ]

    total_quantity = sum(item.quantity for item in items)

    return CartResponse(
        cart_id=str(cart_id),
        user_id=user_id,
        items=response_items,
        total_quantity=total_quantity
    )

@app.post("/cart/items", response_model=CartItemResponse, status_code=201)
async def add_cart_item(payload: CartItemCreate, db: Session = Depends(get_db)):
    product = db.execute(
        text("""
            SELECT product_id, name, base_price
            FROM products
            WHERE product_id = :product_id
        """),
        {"product_id": payload.product_id}
    ).fetchone()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.variant_id is not None:
        variant = db.execute(
            text("""
                SELECT variant_id
                FROM product_variants
                WHERE variant_id = :variant_id AND product_id = :product_id
            """),
            {"variant_id": payload.variant_id, "product_id": payload.product_id}
        ).fetchone()
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found for product")

    cart_row = db.execute(
        text("""
            SELECT cart_id
            FROM carts
            WHERE user_id = :user_id
        """),
        {"user_id": payload.user_id}
    ).fetchone()

    if cart_row:
        cart_id = cart_row.cart_id
    else:
        new_cart = db.execute(
            text("""
                INSERT INTO carts (user_id)
                VALUES (:user_id)
                RETURNING cart_id
            """),
            {"user_id": payload.user_id}
        )
        cart_id = new_cart.scalar()

    existing_item = db.execute(
        text("""
            SELECT cart_item_id, quantity
            FROM cart_items
            WHERE cart_id = :cart_id
              AND product_id = :product_id
              AND ((variant_id IS NULL AND :variant_id IS NULL) OR variant_id = :variant_id)
        """),
        {
            "cart_id": cart_id,
            "product_id": payload.product_id,
            "variant_id": payload.variant_id,
        }
    ).fetchone()

    if existing_item:
        updated_quantity = existing_item.quantity + payload.quantity
        db.execute(
            text("""
                UPDATE cart_items
                SET quantity = :quantity, updated_at = CURRENT_TIMESTAMP
                WHERE cart_item_id = :cart_item_id
            """),
            {"quantity": updated_quantity, "cart_item_id": existing_item.cart_item_id}
        )
        cart_item_id = existing_item.cart_item_id
    else:
        inserted = db.execute(
            text("""
                INSERT INTO cart_items (cart_id, product_id, variant_id, quantity)
                VALUES (:cart_id, :product_id, :variant_id, :quantity)
                RETURNING cart_item_id
            """),
            {
                "cart_id": cart_id,
                "product_id": payload.product_id,
                "variant_id": payload.variant_id,
                "quantity": payload.quantity,
            }
        )
        cart_item_id = inserted.scalar()

    db.commit()

    item = db.execute(
        text("""
            SELECT ci.cart_item_id, ci.cart_id, ci.product_id, ci.quantity, ci.variant_id,
                   p.name AS product_name, p.base_price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.cart_item_id = :cart_item_id
        """),
        {"cart_item_id": cart_item_id}
    ).fetchone()

    return CartItemResponse(
        cart_item_id=str(item.cart_item_id),
        cart_id=str(item.cart_id),
        product_id=str(item.product_id),
        quantity=item.quantity,
        variant_id=str(item.variant_id) if item.variant_id else None,
        product_name=item.product_name,
        base_price=float(item.base_price)
    )

@app.delete("/cart/items/{cart_item_id}", status_code=204)
async def delete_cart_item(cart_item_id: str, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            DELETE FROM cart_items
            WHERE cart_item_id = :cart_item_id
        """),
        {"cart_item_id": cart_item_id}
    )

    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.commit()
    return Response(status_code=204)

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
