# Database Seeding Documentation

## Overview

This document describes the database seeding process, the data generated, and how to use the seeding script.

## Seeding Summary

The database has been seeded with **realistic, complex fake data** using the Faker library to simulate a real e-commerce environment.

### Total Records Created: **1,003 rows**

| Table | Rows | Description |
|-------|------|-------------|
| **categories** | 48 | 8 main categories + 40 subcategories |
| **users** | 51 | 1 admin + 50 customers |
| **addresses** | 109 | 1-3 addresses per user |
| **products** | 101 | Products across all categories |
| **product_variants** | 100 | Variants for ~30% of products |
| **coupons** | 8 | Active discount codes |
| **carts** | 17 | Active shopping carts |
| **cart_items** | 42 | Items in active carts |
| **orders** | 68 | Historical orders |
| **order_items** | 232 | Products in orders |
| **payments** | 68 | Payment transactions |
| **reviews** | 92 | Product reviews |
| **todos** | 66 | Preserved from previous work |

---

## Seeding Script

**File:** `seed_database.py`

### Features

- Generates realistic fake data using Faker
- Creates complex relationships between entities
- Implements business logic (order statuses, payment flows)
- Uses bcrypt for password hashing
- Maintains referential integrity
- Transactional (all-or-nothing)

### Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run seeding script
python seed_database.py
```

---

## Detailed Data Breakdown

### 1. Categories (48 rows)

#### Main Categories (8)
1. **Electronics** - Electronic devices and accessories
2. **Clothing** - Fashion and apparel
3. **Home & Garden** - Home improvement and garden supplies
4. **Sports & Outdoors** - Sports equipment and outdoor gear
5. **Books** - Books and educational materials
6. **Toys & Games** - Toys, games, and hobbies
7. **Health & Beauty** - Health, beauty, and personal care
8. **Food & Beverages** - Food, drinks, and gourmet items

#### Subcategories (40)
Each main category has 5 subcategories:

**Electronics:**
- Smartphones
- Laptops
- Tablets
- Cameras
- Audio

**Clothing:**
- Men's Wear
- Women's Wear
- Kids' Wear
- Shoes
- Accessories

**Home & Garden:**
- Furniture
- Kitchen
- Bathroom
- Garden Tools
- Decor

**Sports & Outdoors:**
- Fitness
- Camping
- Cycling
- Team Sports
- Water Sports

**Books:**
- Fiction
- Non-Fiction
- Educational
- Comics
- Magazines

**Toys & Games:**
- Action Figures
- Board Games
- Puzzles
- Educational Toys
- Video Games

**Health & Beauty:**
- Skincare
- Makeup
- Hair Care
- Vitamins
- Fitness Supplements

**Food & Beverages:**
- Snacks
- Beverages
- Organic
- Gourmet
- International

---

### 2. Users (51 rows)

#### Admin User (1)
- **Email:** `admin@ecommerce.com`
- **Password:** `admin123` (bcrypt hashed)
- **Role:** `admin`
- **Name:** Admin User

#### Customer Users (50)
- **Generated with Faker:**
  - Realistic first and last names
  - Unique email addresses
  - Bcrypt hashed passwords (all: `password123`)
  - Role: `customer`
  - Registration dates: Current timestamp

**Example Users:**
```
Jillian Green - samuelhoffman@example.com
Michael Sparks - santiagostephanie@example.org
Jennifer Clark - elizabethrich@example.net
```

---

### 3. Addresses (109 rows)

Each user has **1-3 addresses**:
- First address is set as default
- Types: `shipping`, `billing`
- Realistic street addresses, cities, postal codes, countries

**Distribution:**
- ~51 users × 2.14 avg addresses = 109 total

**Example:**
```
Street: 123 Main Street
City: New York
Zip: 10001
Country: United States
Type: shipping
```

---

### 4. Products (101 rows)

Products are distributed across subcategories with realistic attributes.

#### Product Templates by Category

**Smartphones:**
- iPhone, Samsung Galaxy, Google Pixel, OnePlus, Xiaomi
- 2-3 variations each

**Laptops:**
- MacBook, Dell XPS, HP Pavilion, Lenovo ThinkPad, ASUS ROG

**Men's Wear:**
- T-Shirt, Jeans, Jacket, Sweater, Polo Shirt

**Women's Wear:**
- Dress, Blouse, Skirt, Cardigan, Leggings

**Furniture:**
- Sofa, Dining Table, Bed Frame, Bookshelf, Office Chair

**Fitness:**
- Yoga Mat, Dumbbells, Resistance Bands, Treadmill, Exercise Ball

**Fiction:**
- Mystery Novel, Romance Novel, Sci-Fi Book, Fantasy Book, Thriller

**Skincare:**
- Face Cream, Cleanser, Serum, Sunscreen, Moisturizer

#### Product Attributes
- **Name:** Product template + optional descriptor
- **Description:** Faker-generated text (200 chars)
- **Base Price:** Random between $19.99 - $999.99
- **VAT Rate:** 23% (0.23)
- **Stock Level:** Random 0-500 units
- **Active Status:** 75% active, 25% inactive

**Example Product:**
```json
{
  "product_id": 1,
  "name": "iPhone",
  "description": "Myself imagine follow card occur individual event...",
  "base_price": 130.09,
  "vat_rate": 0.23,
  "category_id": 57,
  "stock_level": 284,
  "is_active": true
}
```

---

### 5. Product Variants (100 rows)

**30% of products** have variants with different attributes.

#### Variant Types
- **Color:** Red, Blue, Black, White, Green
- **Size:** Small, Medium, Large, XL
- **Material:** Cotton, Polyester, Leather, Metal

#### Variant Attributes
- **Stock Level:** Random 0-100 units
- **Additional Price:** -$5.00 to +$15.00

**Example:**
```
Product: T-Shirt
Variant: Color - Red
Additional Price: +$2.50
Stock: 45 units
```

---

### 6. Coupons (8 rows)

Active promotional codes with different discount types.

| Code | Type | Value | Min Order | Max Usage |
|------|------|-------|-----------|-----------|
| WELCOME10 | percentage | 10% | $0 | 50-500 |
| SAVE20 | percentage | 20% | $50 | 50-500 |
| FLAT50 | fixed | $50 | $100 | 50-500 |
| SUMMER25 | percentage | 25% | $75 | 50-500 |
| FREESHIP | fixed | $10 | $0 | 50-500 |
| MEGA30 | percentage | 30% | $150 | 50-500 |
| FIRST15 | percentage | 15% | $0 | 50-500 |
| LOYALTY5 | fixed | $5 | $0 | 50-500 |

**Validity:**
- Valid from: 1-30 days ago
- Valid until: 30-90 days from now

---

### 7. Shopping Carts (17 rows)

**40% of users** have active shopping carts.

#### Cart Contents
- **Items per cart:** 1-5 products
- **Quantities:** 1-3 units per item
- **Total carts:** 17
- **Total cart items:** 42

**Example Cart:**
```
User: Jillian Green
Items:
  - iPhone × 1
  - Yoga Mat × 2
  - Mystery Novel × 1
```

---

### 8. Orders (68 rows)

**60% of users** have placed orders.

#### Order Distribution
- **Orders per user:** 1-4 orders
- **Total orders:** 68
- **Order date range:** Last 6 months

#### Order Statuses
- `new` - Just placed
- `processing` - Being prepared
- `shipped` - In transit
- `delivered` - Completed (most common)
- `cancelled` - Cancelled

**Status Distribution:**
- Delivered: ~60%
- Processing: ~20%
- Shipped: ~10%
- New: ~10%

#### Order Attributes
- **Items per order:** 1-6 products
- **Total amount:** Sum of (unit_price × quantity)
- **Shipping address:** Random user address
- **Payment:** Linked payment record

**Example Order:**
```json
{
  "order_id": 1,
  "user_id": "5ab6b8be-3af7-46ca-a924-d1f38c02902e",
  "order_date": "2025-08-11 21:57:54",
  "status": "delivered",
  "total_amount": 4983.04,
  "items": 5,
  "payment_status": "paid"
}
```

---

### 9. Order Items (232 rows)

Line items for all orders.

#### Attributes
- **Product:** Reference to product
- **Variant:** Optional variant reference
- **Quantity:** 1-3 units
- **Unit Price:** Price at time of purchase (frozen)

**Average:** 3.4 items per order

---

### 10. Payments (68 rows)

One payment record per order.

#### Payment Methods
- `credit_card` - Most common
- `paypal`
- `bank_transfer`
- `cash_on_delivery`

#### Payment Statuses
- `paid` - Successful payment (most orders)
- `pending` - Awaiting payment (new orders)
- `failed` - Payment failed
- `refunded` - Refunded

**Attributes:**
- **Transaction ID:** UUID
- **Amount:** Matches order total
- **Payment Date:** Same as order date

---

### 11. Reviews (92 rows)

**30% of products** have reviews.

#### Review Distribution
- **Reviews per product:** 1-5 reviews
- **Total reviews:** 92

#### Rating Distribution (weighted)
- (5 stars): 40%
- (4 stars): 30%
- (3 stars): 15%
- (2 stars): 10%
- (1 star): 5%

#### Review Attributes
- **Content:** Faker-generated text (300 chars)
- **Approval Status:** 75% approved, 25% pending
- **User:** Random customer who might have ordered the product

**Example Review:**
```json
{
  "review_id": 1,
  "product_id": 75,
  "user_id": "65fd7075-cdd0-4c1f-958b-6bf180c25cc8",
  "rating": 5,
  "content": "Quality avoid back goal. Beautiful sure head...",
  "is_approved": true
}
```

---

## Technical Details

### Password Hashing

All user passwords are hashed using **bcrypt**:

```python
import bcrypt

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
```

**Default Passwords:**
- Admin: `admin123`
- Customers: `password123`

### Data Generation

Uses **Faker** library for realistic data:

```python
from faker import Faker
fake = Faker()

# Examples
fake.first_name()  # "Jillian"
fake.email()       # "samuelhoffman@example.com"
fake.street_address()  # "123 Main Street"
fake.text(max_nb_chars=200)  # Random text
```

### Referential Integrity

All foreign key relationships are maintained:
- Users → Addresses
- Products → Categories
- Orders → Users, Addresses, Payments
- Order Items → Orders, Products
- Reviews → Products, Users
- Cart Items → Carts, Products

### Transaction Safety

The entire seeding process is wrapped in a transaction:
```python
conn.autocommit = False
try:
    # Seed all tables
    conn.commit()
except:
    conn.rollback()
```

---

## Re-seeding

To re-seed the database:

1. **Drop and recreate tables:**
   ```bash
   python migrate_to_serial.py --confirm
   ```

2. **Run seeding script:**
   ```bash
   python seed_database.py
   ```

**Warning:** This will delete all existing data in e-commerce tables (except `todos`).

---

## Data Verification

After seeding, verify the data:

```bash
# Check all tables and row counts
python check_db_direct.py

# View specific table data in Supabase Dashboard
# Go to: Table Editor > Select table
```

---

## Use Cases

This seeded data supports testing:

1. **User Authentication**
   - Login with admin or customer accounts
   - Password verification

2. **Product Browsing**
   - Category navigation
   - Product search and filtering
   - Variant selection

3. **Shopping Cart**
   - Add/remove items
   - Update quantities
   - Cart persistence

4. **Checkout Process**
   - Address selection
   - Payment processing
   - Order creation

5. **Order Management**
   - Order history
   - Status tracking
   - Order details

6. **Reviews & Ratings**
   - View product reviews
   - Rating aggregation
   - Review moderation

7. **Promotions**
   - Coupon validation
   - Discount calculation
   - Usage tracking

---

## Notes

- All timestamps use UTC timezone
- Prices are in USD (implied)
- VAT rate is 23% for all products
- Stock levels are randomly generated
- Order dates span the last 6 months
- Some products are intentionally inactive (25%)
- Some reviews are pending approval (25%)

---

## Security Considerations

**Production Recommendations:**

1. **Passwords:**
   - Use stronger default passwords
   - Implement password complexity requirements
   - Add password reset functionality

2. **Data:**
   - Don't use seeded data in production
   - Implement proper data validation
   - Add rate limiting

3. **API Keys:**
   - Rotate database passwords regularly
   - Use environment-specific credentials
   - Never commit `.env` to version control

---

## Related Documentation

- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Complete schema documentation
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Setup guide
- [README.md](README.md) - Project overview
