This implementation plan details a structured approach to setting up **pytest** for your FastAPI e-commerce backend, focusing on the proposed testing areas and utilizing standard best practices like fixtures and dependency overriding for isolation.

## Pytest Implementation Plan

The plan is divided into three phases: setting up the core testing infrastructure, creating authentication fixtures, and defining the test execution roadmap.

### Phase 1: Core Testing Infrastructure Setup

This phase focuses on ensuring a clean, isolated environment for every test run, which is crucial when dealing with a transactional database like PostgreSQL.

#### 1.1 Project Structure

We will use the standard Pytest structure within the project root:

```
fastapi-ecommerce/
├── app/
├── database/
├── tests/
│   ├── conftest.py         # Global fixtures (DB, client, auth tokens)
│   ├── test_auth.py        # Authentication and User endpoints
│   ├── test_products.py    # Product Catalog CRUD
│   ├── test_cart.py        # Shopping Cart logic
│   ├── test_orders.py      # Order Processing and Retrieval
│   └── test_promotions.py  # Coupon and Discount testing
└── requirements.txt
```

#### 1.2 Database and Client Fixtures (`tests/conftest.py`)

The heart of the setup is overriding the FastAPI dependency that provides the database session.

| Fixture | Scope | Purpose |
| :--- | :--- | :--- |
| **`test_db`** | `session` | **Database Isolation:** Creates a completely separate test database (`test_ecommerce_db`) at the start of the entire test run, runs schema migration/seeding, and drops it on teardown. This ensures a clean slate for the test suite. |
| **`get_test_session`** | `function` | **Transactional Isolation:** This is the function that **overrides** the production database dependency (`get_db`). It starts a transaction before the test and rolls it back after the test completes, ensuring no test affects the database state for the next test. |
| **`client`** | `function` | Creates the FastAPI `TestClient` instance. It applies the `get_test_session` dependency override to the FastAPI application before yielding the client. |

### Phase 2: Authentication Fixtures

These fixtures streamline testing of protected routes by handling the login process and token management once per module or session.

| Fixture | Scope | Purpose | Required Seeding |
| :--- | :--- | :--- | :--- |
| **`admin_headers`** | `session` | Logs in the admin user (`admin@ecommerce.com`/`admin123`) and retrieves the JWT token. Returns a dictionary: `{"Authorization": "Bearer <token>"}`. | Admin user must be seeded. |
| **`customer_headers`** | `session` | Logs in a standard customer user (e.g., `samuelhoffman@example.com`/`password123`) and returns the necessary authorization header. | At least one customer must be seeded. |

### Phase 3: Test Execution Roadmap

Tests will be organized by domain and will focus on status codes, data integrity, and business logic enforcement (e.g., authorization, calculations).

| Test File | Testing Area | Key Scenarios (Epics) |
| :--- | :--- | :--- |
| **`test_auth.py`** | **Authentication & Users** | **Login/Auth:** Successful login (200), failed login (401). **Profile:** Retrieving current user data (200). **Validation:** Testing Pydantic validation failure (422). |
| **`test_products.py`** | **Product Catalog** | **CRUD Admin:** POST/PUT/DELETE product as admin (201/200/204). **Authorization:** Attempting POST/PUT/DELETE as customer or unauthenticated user (403/401). **GET:** Retrieve product list, filter by category, fetch non-existent product (404). |
| **`test_cart.py`** | **Shopping Cart** | **Items:** Add item to cart, update quantity (0, negative, max stock), remove item. **Totals:** Verify subtotal calculation is accurate after all operations. **Edge Case:** Adding a non-existent product ID (404). |
| **`test_orders.py`** | **Order Processing** | **Creation:** Create an order from a cart, verify cart is cleared, check line item accuracy. **Coupon:** Apply valid/invalid coupon and verify discount calculation. **Authorization:** Customer views *only* their orders. **Admin:** Admin updates order status (e.g., `shipped`). |
| **`test_reviews.py`** | **Reviews & Ratings** | **Submission:** Post a new review with a valid rating (201). **Validation:** Attempting to post a review with an out-of-range rating (422). **Read:** Retrieve all reviews for a specific product. |
| **`test_promotions.py`** | **Promotions & Coupons** | **Coupon Validation:** Test using active, expired, and non-existent coupon codes in a test transaction. **Admin CRUD:** Create a new coupon as an admin. |

### Summary of Implementation

By following this plan, you ensure:

1.  **Isolation:** Every single test runs in a clean, self-contained transaction.
2.  **Efficiency:** Authentication tokens and the database setup are handled once per test session using fixtures.
3.  **Completeness:** All critical business logic (Auth, CRUD, Cart, Orders, Coupons) is covered, focusing not just on success but also on failure and authorization checks.
