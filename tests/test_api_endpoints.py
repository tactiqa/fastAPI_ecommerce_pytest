import os
from typing import Dict, List

import pytest
import requests
from requests import Response
from requests.exceptions import RequestException


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8802").rstrip("/")


@pytest.fixture(scope="session")
def base_url() -> str:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        response.raise_for_status()
    except RequestException as exc:  # pragma: no cover - network dependent
        pytest.skip(f"API is not reachable at {API_BASE_URL}: {exc}")
    return API_BASE_URL


def _get(path: str, *, base_url: str, params: Dict[str, int] | None = None) -> Response:
    return requests.get(f"{base_url}{path}", params=params, timeout=10)


def test_health_endpoint(base_url: str) -> None:
    response = _get("/health", base_url=base_url)
    assert response.status_code == 200

    payload = response.json()
    assert payload.get("status") == "ok"


def test_root_health_check(base_url: str) -> None:
    response = _get("/", base_url=base_url)
    assert response.status_code == 200

    payload = response.json()
    assert payload.get("status") == "healthy"
    assert payload.get("database") == "connected"


def test_stats_endpoint(base_url: str) -> None:
    response = _get("/stats", base_url=base_url)
    assert response.status_code == 200

    stats = response.json()
    assert isinstance(stats, dict)
    assert "products" in stats
    assert "orders" in stats


@pytest.mark.parametrize("path", ["/products", "/orders"])
def test_collection_endpoints_return_lists(base_url: str, path: str) -> None:
    response = _get(path, base_url=base_url, params={"limit": 5})
    assert response.status_code == 200

    items = response.json()
    assert isinstance(items, list)

    if items:  # optional schema sanity check
        assert isinstance(items[0], dict)
