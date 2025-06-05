# tests/test_products.py

import pytest

# Helper to create a product and return its ID and payload
def create_product(client, payload=None):
    if payload is None:
        payload = {
            "name": "Testprodukt",
            "description": "Beskrivelse av testprodukt",
            "price": 199.99,
            "stock": 10
        }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()["id"], payload


def test_create_product(client):
    product_id, payload = create_product(client)
    # Verify via GET
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == payload["name"]
    assert data["stock"] == payload["stock"]


def test_read_product(client):
    product_id, payload = create_product(client)
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["price"] == payload["price"]


def test_update_product(client):
    product_id, _ = create_product(client)
    update_payload = {
        "name": "Endret testprodukt",
        "description": "Oppdatert beskrivelse",
        "price": 249.50,
        "stock": 5
    }
    response = client.put(f"/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == update_payload["name"]
    assert data["stock"] == update_payload["stock"]


def test_delete_product(client):
    product_id, _ = create_product(client)
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404
