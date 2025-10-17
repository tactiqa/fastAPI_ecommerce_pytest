# Testing FastAPI E-commerce Backend with Pytest

To effectively test this FastAPI e-commerce backend with pytest, you should focus on the main functional areas outlined in the project features and structure. Here are the main areas for testing, categorized by functionality:

## 🧪 Main Testing Areas

### 1. Authentication and User Management (Auth/Users)

This is critical for security and access control.

*   **Registration and Login:**
    *   Test successful user (customer and admin) registration.
    *   Test successful login with valid credentials (both admin: `admin@ecommerce.com/admin123` and customer: `samuelhoffman@example.com/password123`).
    *   Test login failure with invalid passwords or non-existent emails.
*   **Access Control (Authorization):**
    *   Test that unauthenticated users cannot access protected routes (e.g., creating a product).
    *   Test that a customer cannot access admin-only routes (e.g., updating a coupon).
    *   Test that an admin can access admin-only routes.
*   **Password Hashing:**
    *   While not testing the bcrypt function directly, ensure that a successfully registered user's password can be verified upon login, confirming correct hashing and comparison.

### 2. Product Catalog and Management (CRUD)

Focus on the core data retrieval and manipulation endpoints.

*   **Read (GET):**
    *   Test retrieving the list of all products (with and without pagination/filtering).
    *   Test retrieving a single product by ID.
    *   Test retrieving products by category.
    *   Test retrieving product variants.
*   **Create, Update, Delete (Admin-only):**
    *   Test creating a new product as an authenticated admin.
    *   Test updating an existing product's details.
    *   Test deleting a product.
    *   Ensure that non-admin users (or unauthenticated users) receive an HTTP 403 Forbidden or 401 Unauthorized when trying to modify products.

### 3. Shopping Cart Functionality

Test the persistent nature and state changes of the shopping cart.

*   **Cart Manipulation:**
    *   Test adding an item (and a specific variant) to a customer's cart.
    *   Test updating the quantity of an item in the cart.
    *   Test removing an item from the cart.
    *   Test retrieving the current state of a customer's cart (and verifying the subtotal calculation).
    *   Test edge cases like adding a non-existent product ID.

### 4. Order Processing and Lifecycle

This involves complex state transitions and calculations.

*   **Order Creation:**
    *   Test creating a new order from a populated shopping cart.
    *   Verify the cart is cleared after a successful order.
    *   Verify the order details (total amount, line items) are correctly stored in the database.
*   **Order Retrieval:**
    *   Test a customer retrieving only their own orders.
    *   Test an admin retrieving all orders.
*   **Status Updates (Admin-only):**
    *   Test updating an order status (e.g., from 'Pending' to 'Shipped').

### 5. Reviews and Ratings

Testing user-submitted content endpoints.

*   **Review Submission:**
    *   Test a customer successfully submitting a review and rating for a product they have purchased (if business logic enforces this).
    *   Test the system handles submission failures (e.g., invalid rating scale).
*   **Review Retrieval:**
    *   Test retrieving all reviews for a specific product.

### 6. Promotions and Coupons

Testing the logic for applying discounts.

*   **Coupon Application:**
    *   Test applying a valid, active coupon (e.g., `WELCOME10`) to a cart or during checkout.
    *   Verify that the correct discount is applied to the order total.
*   **Coupon Failure:**
    *   Test applying an expired or non-existent coupon.
    *   Test applying a coupon that has already been used (if it's a single-use code).

## 🛠️ Recommended Pytest Implementation Approach

The most important part of the setup is ensuring test isolation using:

*   **Fixtures in `tests/conftest.py`:**
    *   **Test Database:** A fixture (`scope="session"` or `scope="module"`) to create and tear down a clean, temporary PostgreSQL database for testing, often by overriding the SQLAlchemy `get_db` dependency.
    *   **Test Client:** A fixture to provide the FastAPI `TestClient`, ensuring it uses the test database dependency override.
    *   **Authenticated Clients:** Fixtures for `admin_client` and `customer_client` that log in using the seeded data (e.g., `admin@ecommerce.com/admin123`) and return the `TestClient` with the valid `Authorization: Bearer <token>` header, making subsequent tests easy to write.
*   **Seeding Data:** Leverage the existing `seed_database.py` script to populate your test database with the 1,069 realistic records before running tests that depend on specific data (like fetching Order ID 68).
*   **Mocking:** Use the `unittest.mock` library (often imported as `mock`) with pytest to mock external services, especially:
    *   The connection to Supabase/PostgreSQL, if necessary, though integration tests that hit the real database are often preferred for backend testing.
    *   Any external payment gateway API calls.
*   **Parametrization:** Use `@pytest.mark.parametrize` to efficiently test multiple cases (e.g., testing all HTTP status codes for validation failures, or testing multiple coupon codes).

You can find more detail on structuring your FastAPI tests and fixtures for user authentication and database isolation here: [Testing A FastAPI App With Pytest](https://www.youtube.com/watch?v=vma91bCgTzM). This video provides an overview of how to set up the `TestClient` and `conftest.py` for FastAPI testing.
