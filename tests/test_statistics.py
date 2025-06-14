# filepath: tests/test_statistics.py
import pytest
import uuid
from datetime import datetime

# Helper to create a customer and product, and place an order

def create_customer(client, admin_headers):
    payload = {
        "first_name": "Stats",
        "last_name": "Tester",
        "email": f"stats.tester+{uuid.uuid4().hex[:6]}@example.com"
    }
    resp = client.post("/customers/", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def create_product(client, admin_headers):
    payload = {
        "name": "StatsProduct",
        "description": "Product for stats testing",
        "price": 123.45,
        "stock": 10
    }
    resp = client.post("/products/", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    return resp.json()["id"], payload["price"]


def create_order(client, user_headers, admin_headers, customer_id, product_id):
    payload = {"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]}
    resp = client.post("/orders/", json=payload, headers=user_headers)
    assert resp.status_code == 201
    return resp.json()["id"], payload


def test_total_users(client, admin_headers):
    resp = client.get("/statistics/total_users", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["count"], int)
    # only the seeded admin exists initially
    assert data["count"] == 1


def test_total_orders_and_unprocessed_count(client, user_headers, admin_headers):
    # create a customer, product, and order
    cust_id = create_customer(client, admin_headers)
    prod_id, price = create_product(client, admin_headers)
    order_id, _ = create_order(client, user_headers, admin_headers, cust_id, prod_id)

    # total_orders should now be 1
    resp_orders = client.get("/statistics/total_orders", headers=admin_headers)
    assert resp_orders.status_code == 200
    assert resp_orders.json()["count"] == 1

    # paid_unprocessed_count: initially still 0
    resp_unprocessed = client.get("/statistics/paid_unprocessed_count", headers=admin_headers)
    assert resp_unprocessed.status_code == 200
    assert resp_unprocessed.json()["count"] == 0

    # Update order to paid
    resp_update = client.put(f"/orders/{order_id}/status", params={"status": "paid"}, headers=admin_headers)
    assert resp_update.status_code == 200

    # Now paid_unprocessed_count should be 1
    resp_unprocessed2 = client.get("/statistics/paid_unprocessed_count", headers=admin_headers)
    assert resp_unprocessed2.status_code == 200
    assert resp_unprocessed2.json()["count"] == 1


def test_unprocessed_orders_list(client, user_headers, admin_headers):
    cust_id = create_customer(client, admin_headers)
    prod_id, price = create_product(client, admin_headers)
    o1, _ = create_order(client, user_headers, admin_headers, cust_id, prod_id)
    o2, _ = create_order(client, user_headers, admin_headers, cust_id, prod_id)
    # mark first as paid
    client.put(f"/orders/{o1}/status", params={"status": "paid"}, headers=admin_headers)
    # leave second pending

    resp = client.get("/statistics/unprocessed_orders", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    # only the paid order(s) appear
    ids = [order["id"] for order in data]
    assert o1 in ids
    assert o2 not in ids
    # orders include customer and items
    order = next(item for item in data if item["id"] == o1)
    assert "customer" in order
    assert "items" in order


def test_total_revenue_and_monthly_sales(client, user_headers, admin_headers):
    cust_id = create_customer(client, admin_headers)
    prod_id, price = create_product(client, admin_headers)
    o_id, _ = create_order(client, user_headers, admin_headers, cust_id, prod_id)
    # Pay order
    client.put(f"/orders/{o_id}/status", params={"status": "paid"}, headers=admin_headers)

    # total_revenue should equal price
    resp_revenue = client.get("/statistics/total_revenue", headers=admin_headers)
    assert resp_revenue.status_code == 200
    total_rev = resp_revenue.json()["total"]
    assert abs(total_rev - price) < 1e-6

    # monthly_sales for current year
    year = datetime.utcnow().year
    resp_sales = client.get(f"/statistics/sales/{year}", headers=admin_headers)
    assert resp_sales.status_code == 200
    sales = resp_sales.json()
    assert isinstance(sales, list)
    # find entry for this month
    current_month = datetime.utcnow().month
    months = [item["month"] for item in sales]
    assert current_month in months
