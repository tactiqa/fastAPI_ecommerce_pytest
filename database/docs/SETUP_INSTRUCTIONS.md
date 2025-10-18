# E-Commerce Database Setup Instructions

## Important Note
Direct database connections may be restricted by network settings. The recommended approach is to use the Supabase Dashboard SQL Editor.

## Setup Methods

### Method 1: Supabase Dashboard (RECOMMENDED)

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Navigate to your project: `rzsdsbdadqufuxfbtymi`

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Execute Schema**
   - Open the file: `sql/create_ecommerce_schema.sql`
   - Copy the entire contents
   - Paste into the SQL Editor
   - Click "Run" or press `Ctrl+Enter`

4. **Verify Tables**
   - Go to "Table Editor" in the left sidebar
   - You should see all 13 tables created

### Method 2: Supabase CLI

If you have Supabase CLI installed:

```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref rzsdsbdadqufuxfbtymi

# Run migrations
supabase db push
```

### Method 3: Python Script (If network allows)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install psycopg2-binary python-dotenv

# Run setup script
python setup_database.py
```

## Tables Created

The schema creates the following 13 tables:

1. **users** - Customer and admin accounts
2. **addresses** - Shipping and billing addresses
3. **categories** - Product categories (hierarchical)
4. **products** - Product catalog
5. **product_variants** - Product variations (size, color, etc.)
6. **carts** - Shopping carts
7. **cart_items** - Items in shopping carts
8. **orders** - Customer orders
9. **order_items** - Items in orders
10. **payments** - Payment transactions
11. **ratings_and_reviews** - Product reviews
12. **discount_coupons** - Promotional codes
13. **coupon_usage** - Coupon usage tracking

## Verify Installation

After running the SQL script, verify the tables:

### Option 1: Using Supabase Dashboard
1. Go to "Table Editor"
2. Check that all 13 tables are listed

### Option 2: Using SQL Query
Run this query in SQL Editor:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

### Option 3: Using Python Script
```bash
python check_db_direct.py
```

## Next Steps

After successful setup:

1. **Review the Schema**
   - Read `DATABASE_SCHEMA.md` for detailed documentation
   - Understand table relationships

2. **Insert Sample Data** (Optional)
   ```sql
   -- Example: Create a test user
   INSERT INTO users (first_name, last_name, email, password_hash, role)
   VALUES ('Test', 'User', 'test@example.com', 'hashed_password', 'customer');
   
   -- Example: Create a category
   INSERT INTO categories (name, description)
   VALUES ('Electronics', 'Electronic devices and accessories');
   ```

3. **Build FastAPI Application**
   - Create API endpoints for each entity
   - Implement CRUD operations
   - Add authentication and authorization

4. **Configure Row Level Security (RLS)**
   - Set up RLS policies in Supabase
   - Protect sensitive data

## Troubleshooting

### Issue: "Network is unreachable"
**Solution:** Use Supabase Dashboard SQL Editor instead of direct connection

### Issue: "Permission denied"
**Solution:** Ensure you're using the SERVICE_ROLE_KEY, not the ANON_KEY

### Issue: "Table already exists"
**Solution:** The schema uses `CREATE TABLE IF NOT EXISTS`, so it's safe to re-run

### Issue: "Foreign key constraint violation"
**Solution:** Check the order of table creation in the SQL file

## Resources

- **Supabase Documentation**: https://supabase.com/docs
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Database Schema**: See `DATABASE_SCHEMA.md`
- **SQL File**: See `sql/create_ecommerce_schema.sql`

## Quick Start Commands

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Check existing tables
python check_db_direct.py

# 4. List tables and row counts
python list_tables_and_rows.py
```

## Security Reminders

1. Never commit `.env` file to version control
2. Use strong password hashing (bcrypt, argon2)
3. Configure RLS policies in Supabase
4. Use ANON_KEY for client-side operations
5. Use SERVICE_ROLE_KEY only on server-side
6. Validate all user inputs
7. Use parameterized queries to prevent SQL injection

## Support

If you encounter issues:
1. Check Supabase project status
2. Verify environment variables in `.env`
3. Review Supabase logs in dashboard
4. Check network connectivity
