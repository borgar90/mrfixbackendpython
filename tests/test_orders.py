# tests/test_orders.py

import pytest
import uuid  # for unique emails

def create_customer(client, payload=None):
    if payload is None:
        payload = {
            "first_name": "Test",
            "last_name": "Kunde",
            "email": f"test.kunde+{uuid.uuid4().hex[:8]}@example.com",
        }
    response = client.post("/customers", json=payload)
    assert response.status_code == 201
    return response.json()["id"]

def create_product(client, payload=None):
    if payload is None:
        payload = {
            "name": "TestOrdreProdukt",
            "description": "Produkt for ordre-testing",
            "price": 50.00,
            "stock": 20
        }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()["id"]

def create_order(client, customer_id=None, product_id=None):
    if customer_id is None:
        customer_id = create_customer(client)
    if product_id is None:
        product_id = create_product(client)
    order_payload = {
        "customer_id": customer_id,
        "items": [
            {"product_id": product_id, "quantity": 2}
        ]
    }
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201
    return response.json()["id"], customer_id, product_id

# Helper to create a customer with a unique email and return its ID
def create_test_customer(client):
    payload = {
        "first_name": "Test",
        "last_name": "Kunde",
        "email": f"test.kunde+{uuid.uuid4().hex[:8]}@example.com"
    }
    response = client.post("/customers", json=payload)
    assert response.status_code == 201
    return response.json()["id"]

def test_create_order(client):
    order_id, customer_id, product_id = create_order(client)
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == customer_id
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2
    assert data["total_amount"] == 100.00

def test_read_order(client):
    order_id, customer_id, product_id = create_order(client)
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) == 1
    assert data["status"] == "pending"

def test_update_order_status(client):
    order_id, _, _ = create_order(client)
    new_status = "paid"
    response = client.put(f"/orders/{order_id}/status", params={"status": new_status})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == new_status

def test_delete_order(client):
    order_id, _, _ = create_order(client)
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 204
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 404
