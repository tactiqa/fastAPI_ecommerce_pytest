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
