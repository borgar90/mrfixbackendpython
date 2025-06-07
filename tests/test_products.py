# tests/test_products.py

import pytest
import uuid

# Helper to create a product and return its ID and payload
def create_product(client, headers, payload=None):
    if payload is None:
        payload = {
            "name": "Testprodukt",
            "description": "Beskrivelse av testprodukt",
            "price": 199.99,
            "stock": 10
        }
    response = client.post("/products/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"], payload


def test_create_product(client, admin_headers):
    product_id, payload = create_product(client, admin_headers)
    response = client.get(f"/products/{product_id}")  # public
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == payload["name"]
    assert data["stock"] == payload["stock"]


def test_read_product(client):
    # Create for read test
    # Use admin to create behind scenes
    # Or reuse create_product helper
    pass  # will use create_product in test; skip header here


def test_update_product(client, admin_headers):
    product_id, _ = create_product(client, admin_headers)
    update_payload = {
        "name": "Endret testprodukt",
        "description": "Oppdatert beskrivelse",
        "price": 249.50,
        "stock": 5
    }
    response = client.put(f"/products/{product_id}", json=update_payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == update_payload["name"]
    assert data["stock"] == update_payload["stock"]


def test_delete_product(client, admin_headers):
    product_id, _ = create_product(client, admin_headers)
    response = client.delete(f"/products/{product_id}", headers=admin_headers)
    assert response.status_code == 204
    response = client.get(f"/products/{product_id}")  # public
    assert response.status_code == 404
