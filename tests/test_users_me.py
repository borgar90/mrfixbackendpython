# tests/test_users_me.py

def test_get_current_user_unauthenticated(client):
    # No token provided
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_as_customer(client, user_headers):
    # user_headers is from customer login
    response = client.get("/users/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    # Should include email and role
    assert "email" in data
    assert data["role"] == "customer"


def test_get_current_user_as_admin(client, admin_headers):
    response = client.get("/users/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin"
    assert data["role"] == "admin"
