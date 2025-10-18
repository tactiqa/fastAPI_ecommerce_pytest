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
        SELECT pv.product_id, pv.variant_id, p.base_price
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
        return {
            "product_id": str(row[0]),
            "variant_id": str(row[1]),
            "base_price": float(row[2]),
        }


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


def test_cart_remove_item_e2e(customer_user_id, product_with_variant):
    """Deleting an item removes it from the cart."""
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
        "quantity": 1,
    }

    create_response = requests.post(f"{BASE_URL}/cart/items", json=payload)
    assert create_response.status_code == 201, create_response.text
    created_item = create_response.json()

    delete_response = requests.delete(f"{BASE_URL}/cart/items/{created_item['cart_item_id']}")
    assert delete_response.status_code == 204

    cart_response = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert cart_response.status_code == 200
    items = cart_response.json()["items"]

    for item in items:
        assert item["cart_item_id"] != created_item["cart_item_id"], "Deleted item still present in cart"


def test_cart_retrieve_state_and_subtotal_e2e(customer_user_id, product_with_variant):
    """GET /cart/{user_id} returns expected totals including subtotal calculation."""
    product_id = product_with_variant["product_id"]
    variant_id = product_with_variant["variant_id"]
    base_price = product_with_variant["base_price"]

    cart_before = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert cart_before.status_code == 200

    for item in cart_before.json()["items"]:
        cleanup = requests.delete(f"{BASE_URL}/cart/items/{item['cart_item_id']}")
        assert cleanup.status_code == 204

    quantity = 3
    payload = {
        "user_id": customer_user_id,
        "product_id": product_id,
        "variant_id": variant_id,
        "quantity": quantity,
    }

    create_response = requests.post(f"{BASE_URL}/cart/items", json=payload)
    assert create_response.status_code == 201, create_response.text
    created_item = create_response.json()

    cart_response = requests.get(f"{BASE_URL}/cart/{customer_user_id}")
    assert cart_response.status_code == 200
    cart_data = cart_response.json()

    assert cart_data["total_quantity"] == quantity
    assert cart_data["user_id"] == customer_user_id

    assert len(cart_data["items"]) == 1
    cart_item = cart_data["items"][0]
    assert cart_item["cart_item_id"] == created_item["cart_item_id"]
    assert cart_item["quantity"] == quantity

    expected_subtotal = base_price * quantity
    actual_subtotal = cart_item["quantity"] * cart_item["base_price"]
    print(
        f"Cart subtotal calculation: quantity={cart_item['quantity']} base_price={cart_item['base_price']} "
        f"=> expected={expected_subtotal} actual={actual_subtotal}"
    )
    assert actual_subtotal == pytest.approx(expected_subtotal, rel=1e-6)

    cleanup_response = requests.delete(f"{BASE_URL}/cart/items/{created_item['cart_item_id']}")
    assert cleanup_response.status_code == 204
