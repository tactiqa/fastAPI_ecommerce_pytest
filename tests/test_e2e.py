import requests

BASE_URL = "http://localhost:8802"

def test_get_single_product_e2e():
    """
    End-to-end test to retrieve a single product from the live API endpoint.
    """
    product_id = 401
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["product_id"] == product_id
    assert product["name"] == "iPhone"

def test_health_check_e2e():
    """
    End-to-end test for the health check endpoint.
    """
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
