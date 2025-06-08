# tests/test_users.py
import pytest
import uuid

# Helper to get admin JWT token
def get_admin_token(client):
    response = client.post(
        "/token", 
        data={"username": "admin", "password": "adminpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# Helper to create a user
def create_user(client, email=None, role="customer", password="secret"):
    if email is None:
        email = f"user+{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": password, "role": role}
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    return data["id"], payload

def test_create_user_and_duplicate(client):
    # Create new user
    user_id, payload = create_user(client)

    # Duplicate email should fail
    response = client.post("/users/", json=payload)
    assert response.status_code == 400

@pytest.fixture
def admin_headers(client):
    token = get_admin_token(client)
    return {"Authorization": f"Bearer {token}"}

# Ensure admin can list users
def test_read_users(client, admin_headers):
    # Create two users
    create_user(client)
    create_user(client)

    response = client.get("/users/", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2

# Ensure admin can get user by ID
def test_read_user_by_id(client, admin_headers):
    user_id, payload = create_user(client)
    response = client.get(f"/users/{user_id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == payload["email"]
    assert data["role"] == payload["role"]

# Ensure admin can update a user
def test_update_user(client, admin_headers):
    user_id, _ = create_user(client)
    new_email = f"updated+{uuid.uuid4().hex[:8]}@example.com"
    update_payload = {"email": new_email, "password": "newpass", "role": "customer"}
    response = client.put(
        f"/users/{user_id}", json=update_payload, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == new_email

# Ensure admin can delete a user
def test_delete_user(client, admin_headers):
    user_id, _ = create_user(client)
    response = client.delete(f"/users/{user_id}", headers=admin_headers)
    assert response.status_code == 204
    # Now fetching should 404
    response = client.get(f"/users/{user_id}", headers=admin_headers)
    assert response.status_code == 404

def test_register_customer_with_shipping(client, admin_headers):
    # Register customer with shipping info
    payload = {
        "email": "shiptest+test@example.com",
        "password": "ship123",
        "role": "customer",
        "shipping": {
            "first_name": "Ship",
            "last_name": "Test",
            "email": "shiptest+test@example.com",
            "address": "1 Shipping Lane",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Norway",
            "phone": "+4711122233"
        }
    }
    # Create user
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    user_id = response.json()["id"]
    # Admin lists customers and should see this new customer
    resp = client.get("/customers/", headers=admin_headers)
    assert resp.status_code == 200
    customers = resp.json()
    assert any(c["email"] == payload["shipping"]["email"] for c in customers)
