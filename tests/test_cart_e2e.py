import os
import uuid

import pytest
import requests
from sqlalchemy import create_engine, text

BASE_URL = "http://localhost:8802"
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    pytest.skip("DATABASE_URL environment variable is required for cart E2E tests", allow_module_level=True)

engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="module")
def customer_user_id():
    """Return an existing customer user ID."""
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT user_id FROM users WHERE role = 'customer' LIMIT 1")
        ).fetchone()
        assert row is not None, "No customer users available for cart tests"
        return str(row[0])


@pytest.fixture(scope="module")
def product_with_variant():
    """Return a product ID with an associated variant ID."""
    query = text(
        """
        SELECT pv.product_id, pv.variant_id
        FROM product_variants pv
        JOIN products p ON p.product_id = pv.product_id
        WHERE p.is_active = TRUE
        ORDER BY pv.product_id, pv.variant_id
        LIMIT 1
        """
    )
    with engine.connect() as connection:
        row = connection.execute(query).fetchone()
        assert row is not None, "No product variants available for cart tests"
        return {"product_id": row[0], "variant_id": row[1]}


def test_cart_add_item_with_variant_e2e(customer_user_id, product_with_variant):
    """POST /cart/items adds an item with variant and cart reflects the addition."""
    product_id = product_with_variant["product_id"]
    variant_id = product_with_variant["variant_id"]

    existing_cart = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert existing_cart.status_code == 200

    for item in existing_cart.json()["items"]:
        if item["product_id"] == product_id and item["variant_id"] == variant_id:
            cleanup = requests.delete(f"{BASE_URL}/cart/items/{item['cart_item_id']}")
            assert cleanup.status_code == 204

    payload = {
        "user_id": customer_user_id,
        "product_id": product_id,
        "variant_id": variant_id,
        "quantity": 2,
    }

    response = requests.post(f"{BASE_URL}/cart/items", json=payload)
    assert response.status_code == 201, response.text
    created_item = response.json()

    assert created_item["product_id"] == product_id
    assert created_item["variant_id"] == variant_id
    assert created_item["quantity"] == payload["quantity"]

    cart_response = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert cart_response.status_code == 200
    cart_data = cart_response.json()
    assert cart_data["user_id"] == customer_user_id

    matching_items = [
        item
        for item in cart_data["items"]
        if item["cart_item_id"] == created_item["cart_item_id"]
    ]
    assert matching_items, "Newly created cart item not present in cart response"

    cleanup_response = requests.delete(f"{BASE_URL}/cart/items/{created_item['cart_item_id']}")
    assert cleanup_response.status_code == 204


def test_cart_update_quantity_e2e(customer_user_id, product_with_variant):
    """Posting the same product again increases the stored quantity."""
    product_id = product_with_variant["product_id"]
    variant_id = product_with_variant["variant_id"]

    existing_cart = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert existing_cart.status_code == 200

    for item in existing_cart.json()["items"]:
        if item["product_id"] == product_id and item["variant_id"] == variant_id:
            cleanup = requests.delete(f"{BASE_URL}/cart/items/{item['cart_item_id']}")
            assert cleanup.status_code == 204

    initial_payload = {
        "user_id": customer_user_id,
        "product_id": product_id,
        "variant_id": variant_id,
        "quantity": 1,
    }

    first_response = requests.post(f"{BASE_URL}/cart/items", json=initial_payload)
    assert first_response.status_code == 201, first_response.text
    first_item = first_response.json()

    assert first_item["quantity"] == initial_payload["quantity"]

    increment_payload = {
        "user_id": customer_user_id,
        "product_id": product_id,
        "variant_id": variant_id,
        "quantity": 2,
    }

    second_response = requests.post(f"{BASE_URL}/cart/items", json=increment_payload)
    assert second_response.status_code == 201, second_response.text
    updated_item = second_response.json()

    assert updated_item["cart_item_id"] == first_item["cart_item_id"]
    assert updated_item["quantity"] == initial_payload["quantity"] + increment_payload["quantity"]

    cart_response = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert cart_response.status_code == 200
    cart_items = cart_response.json()["items"]

    matching = [item for item in cart_items if item["cart_item_id"] == first_item["cart_item_id"]]
    assert matching, "Updated cart item not found in cart"
    assert matching[0]["quantity"] == updated_item["quantity"]

    cleanup_response = requests.delete(f"{BASE_URL}/cart/items/{first_item['cart_item_id']}")
    assert cleanup_response.status_code == 204
