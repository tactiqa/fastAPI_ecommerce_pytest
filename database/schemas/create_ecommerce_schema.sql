-- ============================================================================
-- E-COMMERCE DATABASE SCHEMA
-- ============================================================================
-- This script creates all necessary tables for a complete e-commerce system
-- Compatible with PostgreSQL/Supabase
-- ============================================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
-- Stores information about customers and administrators
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    default_address_id UUID,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================================================
-- 2. ADDRESSES TABLE
-- ============================================================================
-- Stores shipping and billing addresses
CREATE TABLE IF NOT EXISTS addresses (
    address_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    address_type VARCHAR(20) CHECK (address_type IN ('shipping', 'billing', 'both')),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraint to users table for default_address_id
ALTER TABLE users 
ADD CONSTRAINT fk_users_default_address 
FOREIGN KEY (default_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id);

-- ============================================================================
-- 3. CATEGORIES TABLE
-- ============================================================================
-- Hierarchical organization of products
CREATE TABLE IF NOT EXISTS categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(category_id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- ============================================================================
-- 4. PRODUCTS TABLE
-- ============================================================================
-- Stores details about the goods being sold
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    vat DECIMAL(5, 2) DEFAULT 0.00 CHECK (vat >= 0 AND vat <= 100),
    category_id UUID REFERENCES categories(category_id) ON DELETE SET NULL,
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    sku VARCHAR(100) UNIQUE,
    weight DECIMAL(10, 2),
    dimensions VARCHAR(100),
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- ============================================================================
-- 5. PRODUCT_VARIANTS TABLE
-- ============================================================================
-- Handling different attributes of the same product (e.g., size, color)
CREATE TABLE IF NOT EXISTS product_variants (
    variant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    variant_name VARCHAR(50) NOT NULL, -- e.g., 'color', 'size'
    variant_value VARCHAR(50) NOT NULL, -- e.g., 'red', 'XL'
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    additional_price DECIMAL(10, 2) DEFAULT 0.00,
    sku VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, variant_name, variant_value)
);

CREATE INDEX IF NOT EXISTS idx_product_variants_product_id ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_product_variants_sku ON product_variants(sku);

-- ============================================================================
-- 6. CARTS TABLE
-- ============================================================================
-- Storing users' current shopping carts
CREATE TABLE IF NOT EXISTS carts (
    cart_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    session_id VARCHAR(255), -- For guest users
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);
CREATE INDEX IF NOT EXISTS idx_carts_session_id ON carts(session_id);

-- ============================================================================
-- 7. CART_ITEMS TABLE
-- ============================================================================
-- Products contained within a shopping cart
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    variant_id UUID REFERENCES product_variants(variant_id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id, variant_id)
);

CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id);

-- ============================================================================
-- 8. ORDERS TABLE
-- ============================================================================
-- Storing information about placed orders
CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    shipping_address_id UUID REFERENCES addresses(address_id) ON DELETE RESTRICT,
    billing_address_id UUID REFERENCES addresses(address_id) ON DELETE RESTRICT,
    payment_method VARCHAR(50),
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);

-- ============================================================================
-- 9. ORDER_ITEMS TABLE
-- ============================================================================
-- Details of the products included in each order
CREATE TABLE IF NOT EXISTS order_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    variant_id UUID REFERENCES product_variants(variant_id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    vat_rate DECIMAL(5, 2) DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_price DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price - discount_amount) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- ============================================================================
-- 10. PAYMENTS TABLE
-- ============================================================================
-- Recording payment transactions
CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'refunded', 'cancelled')),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL,
    transaction_identifier VARCHAR(255),
    gateway_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_identifier);

-- ============================================================================
-- 11. RATINGS_AND_REVIEWS TABLE
-- ============================================================================
-- Customer feedback on products
CREATE TABLE IF NOT EXISTS ratings_and_reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    content TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON ratings_and_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON ratings_and_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON ratings_and_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_is_approved ON ratings_and_reviews(is_approved);

-- ============================================================================
-- 12. DISCOUNT_COUPONS TABLE
-- ============================================================================
-- Managing promotional codes
CREATE TABLE IF NOT EXISTS discount_coupons (
    coupon_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) CHECK (discount_type IN ('percentage', 'fixed')),
    discount_value DECIMAL(10, 2) NOT NULL CHECK (discount_value >= 0),
    valid_from_date TIMESTAMP NOT NULL,
    valid_to_date TIMESTAMP NOT NULL,
    minimum_order_amount DECIMAL(10, 2) DEFAULT 0.00,
    maximum_usage INTEGER,
    current_usage INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (valid_to_date > valid_from_date)
);

CREATE INDEX IF NOT EXISTS idx_coupons_code ON discount_coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_is_active ON discount_coupons(is_active);

-- ============================================================================
-- 13. COUPON_USAGE TABLE (Additional tracking)
-- ============================================================================
-- Track which users have used which coupons
CREATE TABLE IF NOT EXISTS coupon_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coupon_id UUID NOT NULL REFERENCES discount_coupons(coupon_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(order_id) ON DELETE SET NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(coupon_id, user_id, order_id)
);

CREATE INDEX IF NOT EXISTS idx_coupon_usage_coupon_id ON coupon_usage(coupon_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_user_id ON coupon_usage(user_id);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_addresses_updated_at BEFORE UPDATE ON addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_variants_updated_at BEFORE UPDATE ON product_variants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_carts_updated_at BEFORE UPDATE ON carts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cart_items_updated_at BEFORE UPDATE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON ratings_and_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coupons_updated_at BEFORE UPDATE ON discount_coupons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for product details with category
CREATE OR REPLACE VIEW v_products_with_category AS
SELECT 
    p.*,
    c.name as category_name,
    c.parent_id as category_parent_id
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id;

-- View for order summary
CREATE OR REPLACE VIEW v_order_summary AS
SELECT 
    o.order_id,
    o.user_id,
    u.email as user_email,
    u.first_name || ' ' || u.last_name as user_name,
    o.order_date,
    o.status,
    o.total_amount,
    COUNT(oi.item_id) as item_count,
    p.status as payment_status
FROM orders o
JOIN users u ON o.user_id = u.user_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN payments p ON o.order_id = p.order_id
GROUP BY o.order_id, o.user_id, u.email, u.first_name, u.last_name, 
         o.order_date, o.status, o.total_amount, p.status;

-- ============================================================================
-- SAMPLE DATA (Optional - Comment out if not needed)
-- ============================================================================

-- Insert sample admin user
-- INSERT INTO users (first_name, last_name, email, password_hash, role)
-- VALUES ('Admin', 'User', 'admin@example.com', 'hashed_password_here', 'admin');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
