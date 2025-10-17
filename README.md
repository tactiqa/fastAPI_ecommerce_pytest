# FastAPI E-Commerce Backend

A complete e-commerce backend system built with FastAPI and PostgreSQL (via Supabase), featuring a database schema and seeded data.

## Features

- **Complete Database Schema** - 12 e-commerce tables + legacy todos
- **Realistic Data** - 1,069 rows of seeded data for testing
- **User Management** - Customers and admins with bcrypt passwords
- **Product Catalog** - Categories, products, variants
- **Shopping Cart** - Persistent cart functionality
- **Order Processing** - Complete order lifecycle
- **Reviews & Ratings** - Product feedback system
- **Promotions** - Discount coupons and codes

## Database Stats

- **51 Users** (1 admin: admin@ecommerce.com / admin123)
- **101 Products** across 48 categories
- **68 Orders** with 232 line items
- **92 Reviews** with ratings
- **8 Active Coupons** (WELCOME10, SAVE20, etc.)
- **1,069 Total Records** (excluding legacy todos)

## Project Structure

```
fastapi-ecommerce/
├── app/                          # FastAPI application
│   ├── models/                   # SQLAlchemy models
│   ├── routers/                  # API endpoints
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   ├── utils/                    # Utility functions
│   └── main.py                   # FastAPI app entry point
├── database/                     # Database resources
│   ├── schemas/                  # SQL schema files
│   │   ├── create_ecommerce_schema_v2.sql
│   │   └── create_ecommerce_schema.sql
│   ├── scripts/                  # Database utilities
│   │   ├── check_db_direct.py
│   │   ├── migrate_to_serial.py
│   │   └── seed_database.py
│   └── docs/                     # Database documentation
│       ├── DATABASE_SCHEMA.md
│       ├── DATABASE_SEEDING.md
│       ├── PROJECT_HISTORY.md
│       ├── SETUP_INSTRUCTIONS.md
│       ├── GET_DB_PASSWORD.md
│       └── QUICK_REFERENCE.md
├── docker/                       # Docker configuration
├── tests/                        # Test files
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone git@github.com:tactiqa/API_testing_fastAPI_ecommerce.git
cd fastapi-ecommerce

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
# DATABASE_URL is already configured for the seeded database
```

### 3. Verify Database
```bash
# Check database connection and data
python database/scripts/check_db_direct.py
```

### 4. Reset Database (if needed)
```bash
# Recreate schema and seed fresh data
python database/scripts/migrate_to_serial.py --confirm
python database/scripts/seed_database.py
```

## Admin Access

**Admin Account:**
```
Email: admin@ecommerce.com
Password: admin123
```

**Customer Test Accounts:**
- All customers use password: `password123`
- Sample emails: samuelhoffman@example.com, santiagostephanie@example.org

## Development

### Database Scripts
- **check_db_direct.py** - Verify connection and view data
- **seed_database.py** - Populate with realistic test data
- **migrate_to_serial.py** - Recreate schema from scratch

### Next Steps
1. Create FastAPI application structure in `app/`
2. Implement authentication endpoints
3. Build CRUD operations for products, orders, etc.
4. Add Docker configuration
5. Implement business logic

## Documentation

- **Database Schema** - Complete table definitions in `database/docs/`
- **Seeding Details** - Comprehensive data information
- **Setup Guide** - Step-by-step instructions
- **Quick Reference** - Essential commands and queries

## Docker Support

Docker configuration coming soon in the `docker/` directory.

## Notes

- Database uses SERIAL IDs for simplicity (except user_id as UUID for Supabase Auth)
- All passwords are hashed with bcrypt
- Database is pre-seeded with realistic (but fake) test data
- Ready for FastAPI development
