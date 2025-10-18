import os
import uuid

import pytest
import requests
from sqlalchemy import create_engine, text

BASE_URL = "http://localhost:8802"
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")


if not DATABASE_URL:
    pytest.skip("DATABASE_URL environment variable is required for product E2E tests", allow_module_level=True)


engine = create_engine(DATABASE_URL)

@pytest.fixture(scope="module")
def existing_product_id():
    """Fetch an existing product ID from the seeded database."""
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT product_id FROM products ORDER BY product_id LIMIT 1")
        ).fetchone()
        assert row is not None, "No products available for test"
        return row[0]

def test_get_single_product_e2e(existing_product_id):
    """
    End-to-end test to retrieve a single product from the live API endpoint.
    """
    response = requests.get(f"{BASE_URL}/products/{existing_product_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["product_id"] == existing_product_id

def test_health_check_e2e():
    """
    End-to-end test for the health check endpoint.
    """
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.fixture(scope="module")
def category_id():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT category_id FROM categories ORDER BY category_id LIMIT 1"))
        row = result.fetchone()
        assert row is not None, "No categories available for product tests"
        return row[0]


@pytest.fixture(scope="module")
def product_payload(category_id):
    unique_suffix = uuid.uuid4().hex[:6]
    return {
        "name": f"Test Product {unique_suffix}",
        "description": "End-to-end test product",
        "base_price": 49.99,
        "vat_rate": 0.23,
        "category_id": category_id,
        "stock_level": 5,
        "is_active": True,
    }


@pytest.fixture(scope="module")
def created_product(product_payload):
    response = requests.post(f"{BASE_URL}/products", json=product_payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_01_create_product_e2e(created_product, product_payload):
    assert created_product["name"] == product_payload["name"]
    assert created_product["description"] == product_payload["description"]
    assert created_product["stock_level"] == product_payload["stock_level"]


def test_02_update_product_e2e(created_product, category_id):
    product_id = created_product["product_id"]
    update_payload = {
        "name": f"Updated {created_product['name']}",
        "description": "Updated description",
        "base_price": created_product["base_price"] + 10,
        "vat_rate": 0.23,
        "category_id": category_id,
        "stock_level": created_product["stock_level"] + 1,
        "is_active": True,
    }

    response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_payload)
    assert response.status_code == 200, response.text
    updated_product = response.json()

    assert updated_product["name"] == update_payload["name"]
    assert updated_product["description"] == update_payload["description"]
    assert updated_product["stock_level"] == update_payload["stock_level"]


def test_03_delete_product_e2e(created_product):
    product_id = created_product["product_id"]
    response = requests.delete(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 204, response.text

    follow_up = requests.get(f"{BASE_URL}/products/{product_id}")
    assert follow_up.status_code == 404
