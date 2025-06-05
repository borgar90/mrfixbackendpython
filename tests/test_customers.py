# tests/test_customers.py

import pytest
import uuid  # for unique emails

# Helper to create a customer and return its ID and payload
def create_customer(client, payload=None):
    if payload is None:
        payload = {
            "first_name": "Ola",
            "last_name": "Nordmann",
            "email": f"ola.nordmann+{uuid.uuid4().hex[:8]}@example.com",
            "phone": "99999999",
            "address": "Testveien 1",
            "city": "Oslo",
            "postal_code": "0001",
            "country": "Norge"
        }
    response = client.post("/customers", json=payload)
    assert response.status_code == 201
    return response.json()["id"], payload


def test_create_customer(client):
    customer_id, payload = create_customer(client)
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["first_name"] == payload["first_name"]
    assert data["email"] == payload["email"]


def test_read_customer(client):
    # Each test creates its own customer
    customer_id, payload = create_customer(client)
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["email"] == payload["email"]


def test_update_customer(client):
    customer_id, _ = create_customer(client)
    update_payload = {
        "first_name": "Ole",
        "last_name": "Nordmann",
        "email": "ole.nordmann@example.com",
        "phone": "88888888",
        "address": "Oppdatert vei 2",
        "city": "Bergen",
        "postal_code": "5003",
        "country": "Norge"
    }
    response = client.put(f"/customers/{customer_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["first_name"] == "Ole"
    assert data["email"] == "ole.nordmann@example.com"


def test_delete_customer(client):
    customer_id, _ = create_customer(client)
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 204
    # Bekreft at kunden er borte
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 404
