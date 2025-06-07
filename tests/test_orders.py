# tests/test_orders.py

import pytest
import uuid  # for unique emails

# Helpers to create customer and product
def create_customer(client, headers, payload=None):
    if payload is None:
        payload = {
            "first_name": "Test",
            "last_name": "Kunde",
            "email": f"test.kunde+{uuid.uuid4().hex[:8]}@example.com",
        }
    response = client.post("/customers/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]

def create_product(client, headers, payload=None):
    if payload is None:
        payload = {
            "name": "TestOrdreProdukt",
            "description": "Produkt for ordre-testing",
            "price": 50.00,
            "stock": 20
        }
    response = client.post("/products/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]

# Helper to place an order as a customer
def create_order(client, user_headers, admin_headers, customer_id=None, product_id=None):
    if customer_id is None:
        customer_id = create_customer(client, admin_headers)
    if product_id is None:
        product_id = create_product(client, admin_headers)
    order_payload = {
        "customer_id": customer_id,
        "items": [
            {"product_id": product_id, "quantity": 2}
        ]
    }
    response = client.post("/orders/", json=order_payload, headers=user_headers)
    assert response.status_code == 201
    return response.json()["id"], customer_id, product_id

def test_create_order(client, user_headers, admin_headers):
    order_id, customer_id, product_id = create_order(client, user_headers, admin_headers)
    response = client.get(f"/orders/{order_id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == customer_id
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2
    assert data["total_amount"] == 100.00

def test_read_order(client, user_headers, admin_headers):
    order_id, _, _ = create_order(client, user_headers, admin_headers)
    response = client.get(f"/orders/{order_id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) == 1
    assert data["status"] == "pending"

def test_update_order_status(client, admin_headers, user_headers):
    order_id, _, _ = create_order(client, user_headers, admin_headers)
    new_status = "paid"
    response = client.put(
        f"/orders/{order_id}/status", params={"status": new_status}, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == new_status

def test_delete_order(client, admin_headers, user_headers):
    order_id, _, _ = create_order(client, user_headers, admin_headers)
    response = client.delete(f"/orders/{order_id}", headers=admin_headers)
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f"/orders/{order_id}", headers=user_headers)
    assert response.status_code == 404
