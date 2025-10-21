# E-Commerce Database Schema

## Overview
This document describes the complete database schema for the e-commerce system, including all tables, relationships, and key features.

## Database Tables

### 1. **Users**
Stores information about customers and administrators.

**Columns:**
- `user_id` (UUID, PK) - Unique identifier
- `first_name` (VARCHAR) - User's first name
- `last_name` (VARCHAR) - User's last name
- `email` (VARCHAR, UNIQUE) - User's email address
- `password_hash` (VARCHAR) - Encrypted password
- `role` (VARCHAR) - User role: 'customer' or 'admin'
- `default_address_id` (UUID, FK) - Reference to default address
- `registration_date` (TIMESTAMP) - Account creation date
- `is_active` (BOOLEAN) - Account status
- `phone` (VARCHAR) - Contact phone number

---

### 2. **Addresses**
Stores shipping and billing addresses for users.

**Columns:**
- `address_id` (UUID, PK) - Unique identifier
- `user_id` (UUID, FK) - Reference to user
- `street` (VARCHAR) - Street address
- `city` (VARCHAR) - City name
- `postal_code` (VARCHAR) - Postal/ZIP code
- `country` (VARCHAR) - Country name
- `address_type` (VARCHAR) - Type: 'shipping', 'billing', or 'both'
- `is_default` (BOOLEAN) - Default address flag

---

### 3. **Categories**
Hierarchical organization of products.

**Columns:**
- `category_id` (UUID, PK) - Unique identifier
- `name` (VARCHAR) - Category name
- `description` (TEXT) - Category description
- `parent_id` (UUID, FK) - Reference to parent category (for subcategories)
- `is_active` (BOOLEAN) - Category status
- `display_order` (INTEGER) - Display order

---

### 4. **Products**
Stores details about the goods being sold.

**Columns:**
- `product_id` (UUID, PK) - Unique identifier
- `name` (VARCHAR) - Product name
- `description` (TEXT) - Product description
- `price` (DECIMAL) - Base price
- `vat` (DECIMAL) - VAT/tax percentage
- `category_id` (UUID, FK) - Reference to category
- `stock_quantity` (INTEGER) - Available stock
- `sku` (VARCHAR, UNIQUE) - Stock Keeping Unit
- `weight` (DECIMAL) - Product weight
- `dimensions` (VARCHAR) - Product dimensions
- `image_url` (TEXT) - Product image URL
- `is_active` (BOOLEAN) - Product status
- `date_added` (TIMESTAMP) - Date added to catalog

---

### 5. **Product_Variants**
Handles different attributes of the same product (e.g., size, color).

**Columns:**
- `variant_id` (UUID, PK) - Unique identifier
- `product_id` (UUID, FK) - Reference to product
- `variant_name` (VARCHAR) - Attribute name (e.g., 'color', 'size')
- `variant_value` (VARCHAR) - Attribute value (e.g., 'red', 'XL')
- `stock_quantity` (INTEGER) - Variant-specific stock
- `additional_price` (DECIMAL) - Price adjustment for variant
- `sku` (VARCHAR, UNIQUE) - Variant-specific SKU
- `is_active` (BOOLEAN) - Variant status

---

### 6. **Carts**
Stores users' current shopping carts.

**Columns:**
- `cart_id` (UUID, PK) - Unique identifier
- `user_id` (UUID, FK) - Reference to user (optional for guests)
- `session_id` (VARCHAR) - Session ID for guest users
- `creation_date` (TIMESTAMP) - Cart creation date
- `last_updated_date` (TIMESTAMP) - Last modification date
- `is_active` (BOOLEAN) - Cart status

---

### 7. **Cart_Items**
Products contained within a shopping cart.

**Columns:**
- `cart_item_id` (UUID, PK) - Unique identifier
- `cart_id` (UUID, FK) - Reference to cart
- `product_id` (UUID, FK) - Reference to product
- `variant_id` (UUID, FK) - Reference to product variant (optional)
- `quantity` (INTEGER) - Item quantity
- `added_at` (TIMESTAMP) - Date item was added

---

### 8. **Orders**
Stores information about placed orders.

**Columns:**
- `order_id` (UUID, PK) - Unique identifier
- `user_id` (UUID, FK) - Reference to user
- `order_date` (TIMESTAMP) - Order placement date
- `status` (VARCHAR) - Order status: 'new', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
- `total_amount` (DECIMAL) - Total order amount
- `shipping_address_id` (UUID, FK) - Reference to shipping address
- `billing_address_id` (UUID, FK) - Reference to billing address
- `payment_method` (VARCHAR) - Payment method used
- `shipping_method` (VARCHAR) - Shipping method
- `tracking_number` (VARCHAR) - Shipment tracking number
- `notes` (TEXT) - Order notes

---

### 9. **Order_Items**
Details of the products included in each order.

**Columns:**
- `item_id` (UUID, PK) - Unique identifier
- `order_id` (UUID, FK) - Reference to order
- `product_id` (UUID, FK) - Reference to product
- `variant_id` (UUID, FK) - Reference to product variant (optional)
- `quantity` (INTEGER) - Item quantity
- `unit_price` (DECIMAL) - Price at time of purchase
- `vat_rate` (DECIMAL) - VAT rate applied
- `discount_amount` (DECIMAL) - Discount applied
- `total_price` (DECIMAL, COMPUTED) - Calculated total price

---

### 10. **Payments**
Recording payment transactions.

**Columns:**
- `payment_id` (UUID, PK) - Unique identifier
- `order_id` (UUID, FK) - Reference to order
- `amount` (DECIMAL) - Payment amount
- `status` (VARCHAR) - Payment status: 'pending', 'paid', 'failed', 'refunded', 'cancelled'
- `payment_date` (TIMESTAMP) - Payment date
- `payment_method` (VARCHAR) - Payment method
- `transaction_identifier` (VARCHAR) - Gateway transaction ID
- `gateway_response` (TEXT) - Payment gateway response

---

### 11. **Ratings_and_Reviews**
Customer feedback on products.

**Columns:**
- `review_id` (UUID, PK) - Unique identifier
- `product_id` (UUID, FK) - Reference to product
- `user_id` (UUID, FK) - Reference to user
- `rating` (INTEGER) - Rating (1-5)
- `title` (VARCHAR) - Review title
- `content` (TEXT) - Review content
- `is_approved` (BOOLEAN) - Approval status
- `is_verified_purchase` (BOOLEAN) - Verified purchase flag
- `helpful_count` (INTEGER) - Helpful votes count
- `date_added` (TIMESTAMP) - Review date

---

### 12. **Discount_Coupons**
Managing promotional codes.

**Columns:**
- `coupon_id` (UUID, PK) - Unique identifier
- `code` (VARCHAR, UNIQUE) - Coupon code
- `description` (TEXT) - Coupon description
- `discount_type` (VARCHAR) - Type: 'percentage' or 'fixed'
- `discount_value` (DECIMAL) - Discount value
- `valid_from_date` (TIMESTAMP) - Validity start date
- `valid_to_date` (TIMESTAMP) - Validity end date
- `minimum_order_amount` (DECIMAL) - Minimum order requirement
- `maximum_usage` (INTEGER) - Maximum usage limit
- `current_usage` (INTEGER) - Current usage count
- `is_active` (BOOLEAN) - Coupon status

---

### 13. **Coupon_Usage**
Track which users have used which coupons.

**Columns:**
- `usage_id` (UUID, PK) - Unique identifier
- `coupon_id` (UUID, FK) - Reference to coupon
- `user_id` (UUID, FK) - Reference to user
- `order_id` (UUID, FK) - Reference to order
- `used_at` (TIMESTAMP) - Usage timestamp

---

## Entity Relationship Diagram

```
Users (1) ──< (N) Addresses
Users (1) ──< (N) Orders
Users (1) ──< (N) Carts
Users (1) ──< (N) Ratings_and_Reviews
Users (1) ──< (N) Coupon_Usage

Categories (1) ──< (N) Products
Categories (1) ──< (N) Categories (self-referencing for hierarchy)

Products (1) ──< (N) Product_Variants
Products (1) ──< (N) Cart_Items
Products (1) ──< (N) Order_Items
Products (1) ──< (N) Ratings_and_Reviews

Orders (1) ──< (N) Order_Items
Orders (1) ──< (N) Payments
Orders (1) ──> (1) Addresses (shipping)
Orders (1) ──> (1) Addresses (billing)

Carts (1) ──< (N) Cart_Items

Discount_Coupons (1) ──< (N) Coupon_Usage
```

## Key Features

### 1. **UUID Primary Keys**
All tables use UUID for primary keys, providing better security and scalability.

### 2. **Automatic Timestamps**
All tables include `created_at` and `updated_at` timestamps with automatic triggers.

### 3. **Soft Deletes**
Most tables include `is_active` flags for soft deletion.

### 4. **Referential Integrity**
Foreign key constraints ensure data consistency with appropriate CASCADE and RESTRICT rules.

### 5. **Indexes**
Strategic indexes on frequently queried columns for optimal performance.

### 6. **Computed Columns**
`total_price` in Order_Items is automatically calculated.

### 7. **Check Constraints**
Data validation at the database level (e.g., rating 1-5, positive prices).

### 8. **Views**
Pre-built views for common queries:
- `v_products_with_category` - Products with category information
- `v_order_summary` - Order summary with user and payment details

## Setup Instructions

### 1. **Install Dependencies**
```bash
source venv/bin/activate
pip install psycopg2-binary python-dotenv
```

### 2. **Configure Environment**
Ensure your `.env` file contains:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. **Database Setup**
Use these available scripts:
- `/database/scripts/check_db_direct.py` - for verifying tables
- `/database/scripts/check_schema.py` - for schema validation
- `/database/schemas/create_ecommerce_schema.sql` - the actual SQL schema

### 4. **Verify Tables**
```bash
python database/scripts/check_db_direct.py
```

## Usage Examples

### Insert Sample Data
```sql
-- Insert a category
INSERT INTO categories (name, description)
VALUES ('Electronics', 'Electronic devices and accessories');

-- Insert a product
INSERT INTO products (name, description, price, vat, category_id, stock_quantity)
VALUES ('Laptop', 'High-performance laptop', 999.99, 20.00, 'category-uuid', 50);

-- Insert a product variant
INSERT INTO product_variants (product_id, variant_name, variant_value, stock_quantity)
VALUES ('product-uuid', 'color', 'Silver', 25);
```

### Query Examples
```sql
-- Get all products with categories
SELECT * FROM v_products_with_category WHERE is_active = TRUE;

-- Get order summary
SELECT * FROM v_order_summary WHERE status = 'new';

-- Get product reviews
SELECT * FROM ratings_and_reviews 
WHERE product_id = 'product-uuid' AND is_approved = TRUE
ORDER BY date_added DESC;
```

## Maintenance

### Regular Tasks
1. Monitor table sizes and indexes
2. Archive old orders and carts
3. Clean up expired coupons
4. Review and approve product reviews
5. Update product stock quantities

### Backup Strategy
- Daily automated backups via Supabase
- Export critical data regularly
- Test restore procedures

## Security Considerations

1. **Password Hashing**: Always hash passwords before storing
2. **Row Level Security (RLS)**: Configure RLS policies in Supabase
3. **API Keys**: Never expose service role keys in client code
4. **Input Validation**: Validate all inputs before database operations
5. **SQL Injection**: Use parameterized queries

## Future Enhancements

Potential additions for more advanced features:
- `sessions` - User session management
- `event_logs` - Audit trail
- `favorite_products` - User wishlists
- `shipping_carriers` - Shipping provider details
- `product_attributes` - Flexible attribute system
- `inventory_transactions` - Stock movement tracking
- `notifications` - User notification system
- `product_images` - Multiple images per product
