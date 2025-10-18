# Quick Reference Guide

## Essential Commands

### Database Operations
```bash
# Check database connection and view all tables
python check_db_direct.py

# Re-seed database (WARNING: Deletes existing data)
python seed_database.py

# Recreate schema from scratch
python migrate_to_serial.py --confirm
python seed_database.py
```

### Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version
```

---

## Credentials

### Admin Account
```
Email: admin@ecommerce.com
Password: admin123
```

### Customer Accounts
All customers use password: `password123`

Sample emails:
- samuelhoffman@example.com
- santiagostephanie@example.org
- elizabethrich@example.net

### Database Connection
```
Host: aws-1-eu-west-3.pooler.supabase.com
Port: 6543
Database: postgres
User: postgres.rzsdsbdadqufuxfbtymi
```

---

## Database Quick Facts

### Tables (13)
| Table | Rows | Purpose |
|-------|------|---------|
| categories | 48 | Product categories |
| users | 51 | Customer accounts |
| addresses | 109 | Shipping/billing |
| products | 101 | Product catalog |
| product_variants | 100 | Size/color options |
| carts | 17 | Active carts |
| cart_items | 42 | Cart contents |
| coupons | 8 | Discount codes |
| orders | 68 | Customer orders |
| order_items | 232 | Order details |
| payments | 68 | Transactions |
| reviews | 92 | Product reviews |
| todos | 66 | Legacy data |

**Total: 1,069 rows**

### Active Coupons
| Code | Type | Value | Min Order |
|------|------|-------|-----------|
| WELCOME10 | % | 10% | $0 |
| SAVE20 | % | 20% | $50 |
| FLAT50 | $ | $50 | $100 |
| SUMMER25 | % | 25% | $75 |
| FREESHIP | $ | $10 | $0 |
| MEGA30 | % | 30% | $150 |
| FIRST15 | % | 15% | $0 |
| LOYALTY5 | $ | $5 | $0 |

---

## Important Files

### Configuration
- `.env` - Environment variables (DATABASE_URL, API keys)
- `.env.example` - Template for environment setup
- `requirements.txt` - Python dependencies

### Database
- `sql/create_ecommerce_schema_v2.sql` - Current schema (SERIAL IDs)
- `sql/create_ecommerce_schema.sql` - Original schema (UUID IDs)

### Scripts
- `seed_database.py` - Populate database with fake data
- `migrate_to_serial.py` - Recreate schema
- `check_db_direct.py` - Verify database connection
- `setup_database.py` - Initial database setup

### Documentation
- `README.md` - Project overview
- `DATABASE_SCHEMA.md` - Schema details
- `DATABASE_SEEDING.md` - Seeding details
- `PROJECT_HISTORY.md` - Development log
- `SETUP_INSTRUCTIONS.md` - Setup guide
- `GET_DB_PASSWORD.md` - Database password guide

---

## Common Queries

### Get All Products
```sql
SELECT * FROM v_products_with_category 
WHERE is_active = TRUE 
ORDER BY name;
```

### Get User Orders
```sql
SELECT * FROM v_order_summary 
WHERE user_email = 'admin@ecommerce.com' 
ORDER BY order_date DESC;
```

### Get Product Reviews
```sql
SELECT p.name, r.rating, r.content, u.first_name, u.last_name
FROM reviews r
JOIN products p ON r.product_id = p.product_id
JOIN users u ON r.user_id = u.user_id
WHERE r.is_approved = TRUE
ORDER BY r.created_at DESC;
```

### Get Active Carts
```sql
SELECT u.email, COUNT(ci.cart_item_id) as items
FROM carts c
JOIN users u ON c.user_id = u.user_id
LEFT JOIN cart_items ci ON c.cart_id = ci.cart_id
GROUP BY u.email;
```

### Get Category Hierarchy
```sql
SELECT c1.name as main_category, c2.name as subcategory
FROM categories c1
LEFT JOIN categories c2 ON c1.category_id = c2.parent_id
WHERE c1.parent_id IS NULL
ORDER BY c1.name, c2.name;
```

---

## Troubleshooting

### Connection Issues
```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# Test connection
python check_db_direct.py
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Password Issues
See [GET_DB_PASSWORD.md](GET_DB_PASSWORD.md) for detailed instructions.

### Reset Everything
```bash
# WARNING: This deletes all data!
python migrate_to_serial.py --confirm
python seed_database.py
```

---

## Next Steps

### 1. Build FastAPI Application
```bash
# Create main application file
touch main.py

# Create models directory
mkdir -p app/models
mkdir -p app/routers
mkdir -p app/schemas
```

### 2. Create Pydantic Models
- User schemas (login, register, profile)
- Product schemas (list, detail, create)
- Order schemas (create, list, detail)
- Cart schemas (add, update, checkout)

### 3. Implement Authentication
- JWT token generation
- Login endpoint
- Register endpoint
- Password verification
- Protected routes

### 4. Build CRUD Endpoints
- Products: GET, POST, PUT, DELETE
- Categories: GET
- Cart: POST, PUT, DELETE
- Orders: POST, GET
- Reviews: POST, GET

### 5. Add Business Logic
- Inventory management
- Order processing
- Payment integration
- Email notifications

---

## Useful Links

- [Supabase Dashboard](https://supabase.com/dashboard)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## Support

For issues:
1. Check documentation files
2. Verify environment variables
3. Test database connection
4. Review error messages

---

**Last Updated:** October 16, 2025  
**Database Status:** Seeded and ready  
**Next Milestone:** FastAPI application development
