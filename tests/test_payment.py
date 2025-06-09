# filepath: tests/test_payment.py
import pytest
import uuid
from fastapi.testclient import TestClient
from app.integrations.vipps import VippsClient
from app.integrations.stripe import StripeClient

# Helpers to create customer and product

def create_customer(client: TestClient, headers: dict, payload=None) -> int:
    if payload is None:
        payload = {
            "first_name": "Test",
            "last_name": "Kunde",
            "email": f"test.kunde+{uuid.uuid4().hex[:8]}@example.com",
        }
    res = client.post("/customers/", json=payload, headers=headers)
    assert res.status_code == 201
    return res.json()["id"]


def create_product(client: TestClient, headers: dict, payload=None) -> int:
    if payload is None:
        payload = {
            "name": "TestPaymentProduct",
            "description": "Product for payment tests",
            "price": 10.00,
            "stock": 5
        }
    res = client.post("/products/", json=payload, headers=headers)
    assert res.status_code == 201
    return res.json()["id"]


def create_order(client: TestClient, user_headers: dict, admin_headers: dict):
    customer_id = create_customer(client, admin_headers)
    product_id = create_product(client, admin_headers)
    payload = {"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]}
    res = client.post("/orders/", json=payload, headers=user_headers)
    assert res.status_code == 201
    return res.json()["id"]


def test_vipps_initiate_success(monkeypatch, client, user_headers, admin_headers):
    order_id = create_order(client, user_headers, admin_headers)
    # Stub the VippsClient.create_payment to avoid external calls
    fake_response = {"orderId": str(order_id), "paymentId": "fake12345", "status": "CREATED", "url": "https://mock.vipps/pay"}
    monkeypatch.setattr(VippsClient, "create_payment", lambda self, order_id, amount, callback_url, shipping=None: fake_response)

    request_payload = {
        "order_id": order_id,
        "callback_url": "https://frontend.app/vipps-callback",
        "shipping": {
            "first_name": "Alice",
            "last_name": "Wonderland",
            "address": "Cheshire Cat 1",
            "city": "Oslo",
            "postal_code": "0001",
            "country": "Norway",
            "email": "alice@example.com",
            "phone": "+4790000000"
        }
    }
    resp = client.post("/payment/vipps/initiate", json=request_payload, headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["data"] == fake_response


def test_vipps_initiate_order_not_found(client, user_headers):
    # Attempt initiate on non-existent order
    payload = {"order_id": 9999, "callback_url": "https://app/vipps", "shipping": {"first_name": "A", "last_name": "B", "address": "X", "city": "Y", "postal_code": "Z", "country": "C", "email": "no@exist.com"}}
    resp = client.post("/payment/vipps/initiate", json=payload, headers=user_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Order not found"


# Stripe Payment Tests

def test_stripe_initiate_success(monkeypatch, client, user_headers, admin_headers):
    order_id = create_order(client, user_headers, admin_headers)
    # Stub the StripeClient.create_payment_intent to avoid external calls
    fake_response = {
        "session_id": "cs_test_fake12345",
        "url": "https://checkout.stripe.com/c/pay/cs_test_fake12345",
        "amount": 100,
        "currency": "nok",
        "status": "created",
        "order_id": str(order_id)
    }
    monkeypatch.setattr(StripeClient, "create_payment_intent", lambda self, order_id, amount, callback_url, shipping=None: fake_response)

    request_payload = {
        "order_id": order_id,
        "callback_url": "https://frontend.app/stripe-callback",
        "shipping": {
            "first_name": "Alice",
            "last_name": "Stripe",
            "address": "Stripe Street 1",
            "city": "Oslo",
            "postal_code": "0002",
            "country": "Norway",
            "email": "alice@stripe.example.com",
            "phone": "+4790000001"
        }
    }
    resp = client.post("/payment/stripe/initiate", json=request_payload, headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["data"] == fake_response


def test_stripe_initiate_order_not_found(client, user_headers):
    # Attempt initiate on non-existent order
    payload = {
        "order_id": 9999, 
        "callback_url": "https://app/stripe", 
        "shipping": {
            "first_name": "A", 
            "last_name": "B", 
            "address": "X", 
            "city": "Y", 
            "postal_code": "Z", 
            "country": "C", 
            "email": "no@exist.com"
        }
    }
    resp = client.post("/payment/stripe/initiate", json=payload, headers=user_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Order not found"


def test_stripe_initiate_order_not_pending(monkeypatch, client, user_headers, admin_headers):
    order_id = create_order(client, user_headers, admin_headers)
    
    # Change order status to paid (not pending)
    order_update = {"status": "paid"}
    resp = client.patch(f"/orders/{order_id}", json=order_update, headers=admin_headers)
    assert resp.status_code == 200
    
    # Try to initiate payment on non-pending order
    payload = {
        "order_id": order_id, 
        "callback_url": "https://app/stripe",
        "shipping": {
            "first_name": "A", 
            "last_name": "B", 
            "address": "X", 
            "city": "Y", 
            "postal_code": "Z", 
            "country": "C", 
            "email": "test@stripe.com"
        }
    }
    resp = client.post("/payment/stripe/initiate", json=payload, headers=user_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Order is not pending payment"


# Minimum Amount Validation Tests

def test_vipps_initiate_minimum_amount_validation(client, user_headers, admin_headers):
    # Create an order with amount less than 20 NOK
    customer_id = create_customer(client, admin_headers)
    product_id = create_product(client, admin_headers, {"name": "Low Price Product", "price": 10.0, "stock": 10})
    
    order_payload = {
        "customer_id": customer_id,
        "order_lines": [{"product_id": product_id, "quantity": 1}]
    }
    resp = client.post("/orders/", json=order_payload, headers=user_headers)
    assert resp.status_code == 201
    order_id = resp.json()["id"]
    
    # Try to initiate Vipps payment with amount < 20 NOK
    payload = {
        "order_id": order_id, 
        "callback_url": "https://app/vipps",
        "shipping": {
            "first_name": "A", 
            "last_name": "B", 
            "address": "X", 
            "city": "Y", 
            "postal_code": "Z", 
            "country": "C", 
            "email": "test@vipps.com"
        }
    }
    resp = client.post("/payment/vipps/initiate", json=payload, headers=user_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Order amount must be at least 20 NOK"


def test_stripe_initiate_minimum_amount_validation(client, user_headers, admin_headers):
    # Create an order with amount less than 20 NOK
    customer_id = create_customer(client, admin_headers)
    product_id = create_product(client, admin_headers, {"name": "Low Price Product", "price": 15.0, "stock": 10})
    
    order_payload = {
        "customer_id": customer_id,
        "order_lines": [{"product_id": product_id, "quantity": 1}]
    }
    resp = client.post("/orders/", json=order_payload, headers=user_headers)
    assert resp.status_code == 201
    order_id = resp.json()["id"]
    
    # Try to initiate Stripe payment with amount < 20 NOK
    payload = {
        "order_id": order_id, 
        "callback_url": "https://app/stripe",
        "shipping": {
            "first_name": "A", 
            "last_name": "B", 
            "address": "X", 
            "city": "Y", 
            "postal_code": "Z", 
            "country": "C", 
            "email": "test@stripe.com"
        }
    }
    resp = client.post("/payment/stripe/initiate", json=payload, headers=user_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Order amount must be at least 20 NOK"
