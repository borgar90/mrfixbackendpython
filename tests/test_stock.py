# filepath: tests/test_stock.py
import pytest
import uuid

# Helper to create a new product with initial stock
def create_product(client, headers, payload=None):
    if payload is None:
        payload = {
            "name": f"Prod-{uuid.uuid4().hex[:6]}",
            "description": "Stock test product",
            "price": 10.0,
            "stock": 10
        }
    resp = client.post("/products/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    return data["id"], data

# Helper to create a customer for orders
def create_customer(client, headers, payload=None):
    if payload is None:
        payload = {
            "first_name": "Test",
            "last_name": "Kunde",
            "email": f"test.user+{uuid.uuid4().hex[:8]}@example.com"
        }
    resp = client.post("/customers/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]

# Helper to place an order
def create_order(client, user_headers, admin_headers, customer_id=None, product_id=None):
    if customer_id is None:
        customer_id = create_customer(client, admin_headers)
    if product_id is None:
        product_id, _ = create_product(client, admin_headers)
    payload = {"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 3}]}
    resp = client.post("/orders/", json=payload, headers=user_headers)
    assert resp.status_code == 201
    return resp.json()["id"], product_id


def test_add_stock(client, admin_headers):
    # Add stock to an existing product
    prod_id, orig = create_product(client, admin_headers)
    # Increase by 5
    resp = client.post(f"/products/{prod_id}/stock", json={"quantity": 5}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stock"] == orig["stock"] + 5


def test_remove_stock(client, admin_headers):
    prod_id, orig = create_product(client, admin_headers)
    # Decrease by 4
    resp = client.post(f"/products/{prod_id}/stock", json={"quantity": -4}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stock"] == orig["stock"] - 4


def test_remove_stock_too_much(client, admin_headers):
    prod_id, _ = create_product(client, admin_headers)
    # Attempt to remove more than available
    resp = client.post(f"/products/{prod_id}/stock", json={"quantity": -20}, headers=admin_headers)
    assert resp.status_code == 400
    assert "negative" in resp.json()["detail"]


def test_order_decrements_and_delete_restores_stock(client, user_headers, admin_headers):
    # Create product with known stock
    prod_id, prod = create_product(client, admin_headers, {"name": "StockTest", "description": "","price": 5.0, "stock": 8})
    # Place order for quantity 3
    order_id, _ = create_order(client, user_headers, admin_headers, product_id=prod_id)
    # Verify stock decreased
    resp = client.get(f"/products/{prod_id}")
    assert resp.status_code == 200
    assert resp.json()["stock"] == 8 - 3
    # Delete order
    resp_del = client.delete(f"/orders/{order_id}", headers=admin_headers)
    assert resp_del.status_code == 204
    # Stock should be restored
    resp2 = client.get(f"/products/{prod_id}")
    assert resp2.status_code == 200
    assert resp2.json()["stock"] == 8
