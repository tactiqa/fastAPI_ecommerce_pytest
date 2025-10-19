import os

import pytest
import requests
from sqlalchemy import create_engine, text

BASE_URL = "http://localhost:8802"
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    pytest.skip("DATABASE_URL environment variable is required for order E2E tests", allow_module_level=True)

engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="module")
def customer_details():
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT user_id, email FROM users WHERE role = 'customer' LIMIT 1")
        ).fetchone()
        assert row is not None, "No customer user found for order tests"
        return {"user_id": str(row.user_id), "email": row.email}


@pytest.fixture
def shipping_address_id(customer_details):
    user_id = customer_details["user_id"]
    with engine.begin() as connection:
        existing = connection.execute(
            text(
                """
                SELECT address_id
                FROM addresses
                WHERE user_id = :user_id
                  AND COALESCE(address_type, 'shipping') IN ('shipping', 'both')
                ORDER BY address_id
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        ).fetchone()
        if existing:
            yield str(existing.address_id)
            return
        result = connection.execute(
            text(
                """
                INSERT INTO addresses (user_id, street, city, postal_code, country, address_type)
                VALUES (:user_id, :street, :city, :postal_code, :country, 'shipping')
                RETURNING address_id
                """
            ),
            {
                "user_id": user_id,
                "street": "123 Test Street",
                "city": "Testville",
                "postal_code": "12345",
                "country": "Testland",
            },
        )
        address_id = result.scalar()
    yield str(address_id)
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM addresses WHERE address_id = :address_id"),
            {"address_id": address_id},
        )


@pytest.fixture(scope="module")
def active_product():
    response = requests.get(f"{BASE_URL}/products")
    assert response.status_code == 200, response.text
    products = response.json()
    assert products, "No products available for order tests"
    product = products[0]
    return {
        "product_id": product["product_id"],
        "base_price": float(product["base_price"]),
        "name": product["name"],
    }


@pytest.fixture(scope="module")
def existing_customer_with_orders():
    with engine.connect() as connection:
        customer_row = connection.execute(
            text(
                """
                SELECT u.user_id, u.email
                FROM users u
                WHERE EXISTS (
                    SELECT 1
                    FROM orders o
                    WHERE o.user_id = u.user_id
                )
                ORDER BY u.user_id
                LIMIT 1
                """
            )
        ).fetchone()
        assert customer_row is not None, "No existing customer with orders found"

        orders = connection.execute(
            text(
                """
                SELECT order_id, total_amount
                FROM orders
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                """
            ),
            {"user_id": customer_row.user_id},
        ).fetchall()
        assert orders, "Selected customer has no orders"

    return {
        "user_id": str(customer_row.user_id),
        "email": customer_row.email,
        "orders": {str(order.order_id): float(order.total_amount) for order in orders},
    }


def clear_cart(user_id: str):
    with engine.begin() as connection:
        cart_row = connection.execute(
            text("SELECT cart_id FROM carts WHERE user_id = :user_id"),
            {"user_id": user_id},
        ).fetchone()
        if cart_row:
            connection.execute(
                text("DELETE FROM cart_items WHERE cart_id = :cart_id"),
                {"cart_id": cart_row.cart_id},
            )


def test_create_order_from_cart_e2e(customer_details, shipping_address_id, active_product):
    user_id = customer_details["user_id"]
    product_id = active_product["product_id"]
    base_price = active_product["base_price"]
    quantity = 2

    clear_cart(user_id)

    add_response = requests.post(
        f"{BASE_URL}/cart/items",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )
    assert add_response.status_code == 201, add_response.text
    cart_item = add_response.json()
    assert cart_item["product_id"] == product_id
    assert cart_item["quantity"] == quantity

    order_response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "user_id": user_id,
            "shipping_address_id": shipping_address_id,
        },
    )
    assert order_response.status_code == 201, order_response.text
    order_data = order_response.json()
    order_id = order_data["order_id"]

    assert order_data["customer_email"] == customer_details["email"]
    assert order_data["order_status"] == "new"
    assert order_data["total_amount"] == pytest.approx(base_price * quantity, rel=1e-6)

    assert len(order_data["items"]) == 1
    order_item = order_data["items"][0]
    assert order_item["product_id"] == product_id
    assert order_item["quantity"] == quantity
    assert order_item["unit_price"] == pytest.approx(base_price, rel=1e-6)

    with engine.connect() as connection:
        db_order = connection.execute(
            text(
                """
                SELECT total_amount
                FROM orders
                WHERE order_id = :order_id
                """
            ),
            {"order_id": order_id},
        ).fetchone()
        assert db_order is not None, "Order record not persisted"
        assert float(db_order.total_amount) == pytest.approx(base_price * quantity, rel=1e-6)

        db_order_items = connection.execute(
            text(
                """
                SELECT product_id, quantity, unit_price
                FROM order_items
                WHERE order_id = :order_id
                ORDER BY order_item_id
                """
            ),
            {"order_id": order_id},
        ).fetchall()
        assert len(db_order_items) == 1
        db_item = db_order_items[0]
        assert str(db_item.product_id) == product_id
        assert db_item.quantity == quantity
        assert float(db_item.unit_price) == pytest.approx(base_price, rel=1e-6)

    cart_response = requests.get(f"{BASE_URL}/cart/{user_id}")
    assert cart_response.status_code == 200, cart_response.text
    cart_data = cart_response.json()
    assert cart_data["items"] == []
    assert cart_data["total_quantity"] == 0

    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM order_items WHERE order_id = :order_id"),
            {"order_id": order_id},
        )
        connection.execute(
            text("DELETE FROM orders WHERE order_id = :order_id"),
            {"order_id": order_id},
        )
    clear_cart(user_id)


def test_user_orders_endpoint_returns_existing_orders(existing_customer_with_orders):
    user_id = existing_customer_with_orders["user_id"]
    expected_email = existing_customer_with_orders["email"]
    expected_totals = existing_customer_with_orders["orders"]

    response = requests.get(f"{BASE_URL}/users/{user_id}/orders")
    assert response.status_code == 200, response.text

    orders = response.json()
    assert orders, "Endpoint returned no orders for customer with known orders"

    response_ids = {order["order_id"] for order in orders}
    assert response_ids.issubset(expected_totals.keys())

    for order in orders:
        assert order["customer_email"] == expected_email
        assert order["order_id"] in expected_totals
        assert order["total_amount"] == pytest.approx(expected_totals[order["order_id"]], rel=1e-6)


def test_user_orders_endpoint_returns_only_customer_orders(customer_details, shipping_address_id, active_product):
    user_id = customer_details["user_id"]
    product_id = active_product["product_id"]
    base_price = active_product["base_price"]
    quantity = 2

    clear_cart(user_id)

    add_response = requests.post(
        f"{BASE_URL}/cart/items",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )
    assert add_response.status_code == 201, add_response.text
    cart_item = add_response.json()
    assert cart_item["product_id"] == product_id
    assert cart_item["quantity"] == quantity

    order_response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "user_id": user_id,
            "shipping_address_id": shipping_address_id,
        },
    )
    assert order_response.status_code == 201, order_response.text
    order_data = order_response.json()
    order_id = order_data["order_id"]

    assert order_data["customer_email"] == customer_details["email"]
    assert order_data["order_status"] == "new"
    assert order_data["total_amount"] == pytest.approx(base_price * quantity, rel=1e-6)

    assert len(order_data["items"]) == 1
    order_item = order_data["items"][0]
    assert order_item["product_id"] == product_id
    assert order_item["quantity"] == quantity
    assert order_item["unit_price"] == pytest.approx(base_price, rel=1e-6)

    with engine.connect() as connection:
        db_order = connection.execute(
            text(
                """
                SELECT total_amount
                FROM orders
                WHERE order_id = :order_id
                """
            ),
            {"order_id": order_id},
        ).fetchone()
        assert db_order is not None, "Order record not persisted"
        assert float(db_order.total_amount) == pytest.approx(base_price * quantity, rel=1e-6)

        db_order_items = connection.execute(
            text(
                """
                SELECT product_id, quantity, unit_price
                FROM order_items
                WHERE order_id = :order_id
                ORDER BY order_item_id
                """
            ),
            {"order_id": order_id},
        ).fetchall()
        assert len(db_order_items) == 1
        db_item = db_order_items[0]
        assert str(db_item.product_id) == product_id
        assert db_item.quantity == quantity
        assert float(db_item.unit_price) == pytest.approx(base_price, rel=1e-6)

    cart_response = requests.get(f"{BASE_URL}/cart/{user_id}")
    assert cart_response.status_code == 200, cart_response.text
    cart_data = cart_response.json()
    assert cart_data["items"] == []
    assert cart_data["total_quantity"] == 0

    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM order_items WHERE order_id = :order_id"),
            {"order_id": order_id},
        )
        connection.execute(
            text("DELETE FROM orders WHERE order_id = :order_id"),
            {"order_id": order_id},
        )
    clear_cart(user_id)
