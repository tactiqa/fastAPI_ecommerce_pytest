# FastAPI E-Commerce API Python/Pytest Test Suite

This repository is a set of python/pytest based test suites for a realistic FastAPI e-commerce backend. The backend build with FastAPI runs inside Docker container that uses Supabase/PostgreSQL as the database for all ecommerce data. The application thips with a full Supabase/PostgreSQL schema, seeded data, and a growing suite of automated tests that demonstrate how to validate APIs,

## Repository layout (testing-focused)

```
fastapi-ecommerce/
├── app/                          # FastAPI application (tests target these endpoints)
├── database/
│   ├── scripts/                  # Helper scripts for DB verification & seeding
│   └── docs/                     # Schema reference used by tests
├── docs/testing/                 # Testing strategy & implementation guides
├── docker/                       # Compose files for API + Postgres
├── tests/
│   ├── test_cart_e2e.py          # Cart lifecycle scenarios
│   ├── test_orders_e2e.py        # Order creation & retrieval flows
│   ├── test_product_e2e.py       # Product CRUD & filtering checks
│   └── test_api_endpoints.py     # Smoke tests and basic contract checks
├── requirements.txt              # Pin pytest + tooling dependencies
└── README_00.md                  # (This document) Testing-first overview
```

## Getting started with testing

### 1. Environment bootstrap

```bash
git clone git@github.com:tactiqa/fastAPI_ecommerce_pytest.git
cd fastAPI_ecommerce_pytest
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env 
```

**Configure .env file:**
Update the `.env` file with your database credentials:
- `DATABASE_URL`: supabase database connection string (Transaction pooler)
- `SUPABASE_URL`: supabase URL project
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

### 2. Bring the stack online (Docker + Supabase)

```bash
cd docker
docker compose up -d
cd ..
```

Verify the API (adjust your port if needed in docker-compose.yml):

```bash
curl http://localhost:8802/health
```

### 3. Inspect seeded data (optional but recommended)

```bash
./venv/bin/python database/scripts/check_db_direct.py
```

### 4. Run the full pytest suite

```bash
./venv/bin/python -m pytest -v
```

Key testsuites:

- `tests/test_cart_e2e.py` demonstrates idempotent setup/cleanup when manipulating carts.
- `tests/test_orders_e2e.py` blends HTTP calls with SQL assertions to confirm persistence.
- `tests/test_product_e2e.py` covers happy-path CRUD plus error contracts.

### 5. Targeted test execution

Run a single test module:

```bash
./venv/bin/python -m pytest tests/test_orders_e2e.py -vv
```

Run an individual test case:

```bash
./venv/bin/python -m pytest tests/test_orders_e2e.py::test_user_orders_endpoint_returns_existing_orders -vv
```

## Working with the database helper scripts

Seed your SQL database (supabase) before running pytest (seed_database.py)

- `database/scripts/check_db_direct.py`: quick snapshot of table counts and sample rows.
- `database/scripts/migrate_to_serial.py --confirm`: rebuild schema locally before reseeding.
- `database/scripts/seed_database.py`: repopulate with canonical seed data.


## endpoints under test

- `GET /health`: API heartbeat (smoke test).
- `GET /products`, `POST /products`: coverage in `test_product_e2e.py`.
- `POST /cart/items`, `GET /cart/{user_id}`: exercised by cart E2E flows.
- `POST /orders`: creates an order from the cart and clears cart contents.
- `GET /users/{user_id}/orders`: newly added endpoint returning customer-specific order history.

## Credentials & test identities

- **Admin**: `admin@ecommerce.com` / `admin123`
- **Customers**: all seeded customers share password `password123` (see `/extra_docs/DATABASE_SEEDING.md` for emails).

## Troubleshooting tips

- If pytest cannot connect to the API, ensure the Docker compose stack is running and ports are free.
- The FastAPI backend container connects to the Supabase-hosted PostgreSQL instance via the `DATABASE_URL` value in `.env`; confirm credentials and network access if connections fail.
- If database queries fail, confirm `DATABASE_URL` is correct and environment variables are loaded (`cp .env.example .env`).
- For flaky tests, re-run with `-vv --maxfail=1` to get detailed logs and abort early.

```bash
./venv/bin/python -m pytest -vv --maxfail=1
```