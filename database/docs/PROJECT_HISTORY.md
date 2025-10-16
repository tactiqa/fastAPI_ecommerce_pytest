# Project History & Development Log

## Overview

This document chronicles the complete development process of the FastAPI E-Commerce system, from initial setup to the current state with a fully seeded database.

---

## 📅 Development Timeline

### Phase 1: Initial Setup (Session Start)

#### 1.1 Environment Configuration
**Goal:** Set up Python virtual environment and configure Supabase connection

**Actions:**
- Created Python virtual environment in `/home/minixu/coding/pytest/fastapi-ecommerce/`
- Configured `.env` file with Supabase credentials:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_ANON_KEY`
  - `DATABASE_URL` (Transaction Pooler connection)

**Files Created:**
- `venv/` - Python virtual environment
- `.env` - Environment variables
- `.env.example` - Template for environment variables

**Challenges:**
- Initial connection attempts failed with direct connection
- Resolved by using Supabase Transaction Pooler (port 6543)
- Required database password instead of service role key

---

### Phase 2: Database Schema Design

#### 2.1 Initial Schema (UUID-based)
**Goal:** Create comprehensive e-commerce database schema

**Actions:**
- Designed 13 core tables with UUID primary keys
- Implemented foreign key relationships
- Added indexes for performance
- Created automatic timestamp triggers
- Built views for common queries

**Files Created:**
- `sql/create_ecommerce_schema.sql` - Original UUID-based schema
- `setup_database.py` - Database setup script
- `DATABASE_SCHEMA.md` - Schema documentation

**Tables Created:**
1. users
2. addresses
3. categories
4. products
5. product_variants
6. carts
7. cart_items
8. orders
9. order_items
10. payments
11. ratings_and_reviews
12. discount_coupons
13. coupon_usage

#### 2.2 Schema Migration (UUID → SERIAL)
**Goal:** Simplify schema by using SERIAL IDs instead of UUIDs

**Rationale:**
- Simpler integer-based IDs for most tables
- Better performance for joins and indexes
- Easier to work with in APIs
- UUID kept only for `user_id` (Supabase Auth compatibility)

**Actions:**
- Created new schema with SERIAL primary keys
- Developed migration script to drop old tables
- Preserved existing `todos` table (66 rows)
- Updated all foreign key relationships

**Files Created:**
- `sql/create_ecommerce_schema_v2.sql` - SERIAL-based schema
- `migrate_to_serial.py` - Migration script

**Migration Results:**
- Successfully migrated all tables
- Preserved todos table data
- All foreign keys updated correctly

---

### Phase 3: Database Connection & Verification

#### 3.1 Connection Scripts
**Goal:** Create utilities to verify database connectivity and inspect tables

**Actions:**
- Developed direct database connection script
- Created table listing and row counting utilities
- Implemented connection using Transaction Pooler

**Files Created:**
- `check_db_direct.py` - Direct database connection checker
- `list_tables_and_rows.py` - Table listing script
- `check_tables.py` - Table verification script
- `GET_DB_PASSWORD.md` - Database password guide

**Connection Details:**
```
Host: aws-1-eu-west-3.pooler.supabase.com
Port: 6543 (Transaction Pooler)
Database: postgres
User: postgres.rzsdsbdadqufuxfbtymi
```

#### 3.2 Existing Data Discovery
**Finding:** Database already contained a `todos` table with 66 rows

**Decision:** Preserve the existing todos table alongside new e-commerce tables

**Result:** Coexistence of legacy and new tables in same schema

---

### Phase 4: Database Seeding

#### 4.1 Seeding Script Development
**Goal:** Populate database with realistic, complex fake data for testing

**Actions:**
- Installed Faker library for data generation
- Installed bcrypt for password hashing
- Developed comprehensive seeding script
- Implemented business logic (order statuses, payment flows)
- Created hierarchical categories
- Generated realistic user data
- Created complex order histories

**Files Created:**
- `seed_database.py` - Database seeding script
- Updated `requirements.txt` with Faker and bcrypt

**Dependencies Added:**
```
faker==22.6.0
passlib[bcrypt]==1.7.4
bcrypt==5.0.0
```

#### 4.2 Seeding Execution
**Date:** October 16, 2025, 9:46 PM UTC+2

**Data Generated:**
- 48 categories (8 main + 40 subcategories)
- 51 users (1 admin + 50 customers)
- 109 addresses
- 101 products across all categories
- 100 product variants
- 8 promotional coupons
- 17 active shopping carts
- 42 cart items
- 68 orders (last 6 months)
- 232 order items
- 68 payment transactions
- 92 product reviews

**Total Records:** 1,003 rows (excluding todos)

**Seeding Time:** ~2 seconds

---

## 🏗️ Architecture Decisions

### 1. ID Strategy

**Decision:** Use SERIAL for most tables, UUID only for users

**Reasoning:**
- SERIAL (auto-increment integers) are simpler and more performant
- UUIDs for users maintain compatibility with Supabase Auth
- Integer IDs are easier to work with in REST APIs
- Better join performance with integer keys

### 2. Password Security

**Decision:** Use bcrypt for password hashing

**Implementation:**
```python
import bcrypt

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
```

**Reasoning:**
- Industry standard for password hashing
- Built-in salt generation
- Configurable work factor
- Resistant to rainbow table attacks

### 3. Database Connection

**Decision:** Use Transaction Pooler instead of direct connection

**Reasoning:**
- Better for stateless applications
- Connection pooling for performance
- IPv4 compatible (direct connection had IPv6 issues)
- Recommended by Supabase for most use cases

### 4. Data Seeding Strategy

**Decision:** Generate realistic fake data with complex relationships

**Reasoning:**
- Enables realistic testing scenarios
- Tests foreign key constraints
- Validates business logic
- Provides diverse data for development
- Simulates real-world usage patterns

---

## 📊 Current Database State

### Tables Overview

| Table | Rows | Primary Key | Status |
|-------|------|-------------|--------|
| categories | 48 | SERIAL | ✅ Seeded |
| users | 51 | UUID | ✅ Seeded |
| addresses | 109 | SERIAL | ✅ Seeded |
| products | 101 | SERIAL | ✅ Seeded |
| product_variants | 100 | SERIAL | ✅ Seeded |
| carts | 17 | SERIAL | ✅ Seeded |
| cart_items | 42 | SERIAL | ✅ Seeded |
| coupons | 8 | SERIAL | ✅ Seeded |
| orders | 68 | SERIAL | ✅ Seeded |
| order_items | 232 | SERIAL | ✅ Seeded |
| payments | 68 | SERIAL | ✅ Seeded |
| reviews | 92 | SERIAL | ✅ Seeded |
| todos | 66 | INTEGER | ✅ Preserved |

### Views

- `v_products_with_category` - Products with category information
- `v_order_summary` - Order summaries with user and payment details

---

## 🔧 Technical Stack

### Backend
- **Database:** PostgreSQL (via Supabase)
- **Connection:** psycopg2-binary
- **ORM:** Direct SQL (no ORM yet)

### Development Tools
- **Python:** 3.13
- **Virtual Environment:** venv
- **Environment Management:** python-dotenv

### Data Generation
- **Faker:** 37.11.0 - Realistic fake data
- **bcrypt:** 5.0.0 - Password hashing

### Planned (Not Yet Implemented)
- **FastAPI:** Web framework
- **Pydantic:** Data validation
- **JWT:** Authentication
- **pytest:** Testing

---

## 📝 Documentation Created

### Core Documentation
1. **README.md** - Project overview and quick start
2. **DATABASE_SCHEMA.md** - Detailed schema documentation
3. **DATABASE_SEEDING.md** - Seeding process and data details
4. **SETUP_INSTRUCTIONS.md** - Setup guide
5. **GET_DB_PASSWORD.md** - Database password guide
6. **PROJECT_HISTORY.md** - This file

### Technical Documentation
- SQL schema files with inline comments
- Python scripts with docstrings
- Environment variable templates

---

## 🎯 Next Steps

### Immediate (Ready to Implement)
1. **FastAPI Application Structure**
   - Create main application file
   - Set up routing
   - Configure CORS

2. **Database Models (Pydantic)**
   - Create schemas for all entities
   - Add validation rules
   - Define request/response models

3. **Authentication System**
   - JWT token generation
   - Login/register endpoints
   - Password verification
   - Role-based access control

### Short Term
4. **CRUD Endpoints**
   - Products (list, get, create, update, delete)
   - Categories (list, get)
   - Users (profile, update)
   - Cart (add, remove, update, checkout)

5. **Business Logic**
   - Order creation workflow
   - Payment processing integration
   - Inventory management
   - Coupon validation

6. **Testing**
   - Unit tests for business logic
   - Integration tests for API endpoints
   - Test with seeded data

### Long Term
7. **Advanced Features**
   - Search and filtering
   - Product recommendations
   - Email notifications
   - Admin dashboard
   - Analytics and reporting

8. **Performance Optimization**
   - Query optimization
   - Caching strategy
   - API rate limiting
   - Database indexing review

9. **Deployment**
   - Docker containerization
   - CI/CD pipeline
   - Production environment setup
   - Monitoring and logging

---

## 🐛 Issues Encountered & Resolutions

### Issue 1: Database Connection Failed
**Problem:** Initial connection attempts using direct connection (port 5432) failed

**Error:** `Network is unreachable` and `duplicate SASL authentication request`

**Solution:** 
- Switched to Transaction Pooler (port 6543)
- Used DATABASE_URL environment variable
- Required actual database password, not service role key

### Issue 2: Password Hashing Error
**Problem:** passlib bcrypt integration had compatibility issues

**Error:** `password cannot be longer than 72 bytes`

**Solution:**
- Switched from passlib to direct bcrypt usage
- Implemented custom hash_password function
- Properly encoded passwords to bytes

### Issue 3: UUID vs SERIAL Decision
**Problem:** Initial schema used UUIDs for all tables, adding complexity

**Decision:** Migrate to SERIAL IDs for simplicity

**Implementation:**
- Created migration script
- Preserved user_id as UUID for Supabase Auth
- All other tables use SERIAL

---

## 📈 Statistics

### Code Metrics
- **Python Files:** 8 scripts
- **SQL Files:** 2 schemas
- **Documentation Files:** 6 markdown files
- **Total Lines of Code:** ~2,500+

### Database Metrics
- **Tables:** 13 (12 e-commerce + 1 legacy)
- **Views:** 2
- **Indexes:** 25+
- **Triggers:** 11 (automatic timestamps)
- **Foreign Keys:** 20+

### Data Metrics
- **Total Rows:** 1,069 (1,003 seeded + 66 todos)
- **Users:** 51
- **Products:** 101
- **Orders:** 68
- **Reviews:** 92

---

## 🤝 Collaboration Notes

### Admin Credentials
```
Email: admin@ecommerce.com
Password: admin123
```

### Customer Test Accounts
All customer accounts use password: `password123`

Sample emails:
- samuelhoffman@example.com
- santiagostephanie@example.org
- elizabethrich@example.net

### Database Access
```bash
# Connection string format
postgresql://postgres.rzsdsbdadqufuxfbtymi:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres

# Verify connection
python check_db_direct.py
```

---

## 🔄 Version History

### v0.1.0 - Initial Setup
- Virtual environment created
- Supabase connection configured
- Basic scripts created

### v0.2.0 - UUID Schema
- Complete e-commerce schema with UUIDs
- 13 tables created
- Foreign keys and indexes added

### v0.3.0 - SERIAL Migration
- Migrated to SERIAL IDs
- Preserved user_id as UUID
- Updated all relationships

### v0.4.0 - Database Seeding (Current)
- Comprehensive seeding script
- 1,000+ realistic records
- Complex relationships
- Ready for API development

---

## 📚 References

### Technologies Used
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

### Design Patterns
- Repository pattern (planned for data access)
- Service layer pattern (planned for business logic)
- DTO pattern (Pydantic models)

---

**Last Updated:** October 16, 2025, 9:49 PM UTC+2  
**Status:** Database seeded, ready for FastAPI development  
**Next Milestone:** Create FastAPI application structure
