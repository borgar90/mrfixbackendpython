# tests/conftest.py

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # use StaticPool for in-memory DB persistence

from app.database import Base, get_db
from app.main import app as fastapi_app
# Import models so Base.metadata knows all tables (alias to avoid shadowing 'app')
import app.models as _models

# ---------------------------------------------------------------
# Konfigurasjon for testdatabase (SQLite in-memory for testformål)
# ---------------------------------------------------------------

# Bruk en SQLite in-memory DB for testing, slik at vi ikke polutterer produksjons-DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Opprett en egen engine for tests
engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# ---------------------------------------------------------------
# Overskriv FastAPI sin get_db-dependency slik at den bruker test-DB
# ---------------------------------------------------------------
def override_get_db():
    """
    Returnerer en session koblet til in-memory SQLite for tests.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Siden vi allerede har importert modellene ovenfor, blir Base.metadata oppdatert
# Sørg for at tabellene blir opprettet i test-databasen før vi kjører tester
Base.metadata.create_all(bind=engine_test)

# Override dependency i FastAPI (get_db) med vår override_get_db
fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def client():
    """
    TestClient–fixture for å sende HTTP-forespørsler til FastAPI-appen.
    Scope 'session' slik at vi gjenbruker client for alle tester i hele testkjøringen.
    """
    with TestClient(fastapi_app) as test_client:
        yield test_client

# Ensure each test runs with a fresh database
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    # Seed default admin with valid email for test database
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    from app.models import User
    from app.schemas import UserRole
    from app.crud.users import pwd_context
    db = TestingSessionLocal()
    admin_hashed = pwd_context.hash("adminpass")
    db.add(User(email=ADMIN_EMAIL, hashed_password=admin_hashed, role=UserRole.admin.value))
    db.commit()
    db.close()
    yield

@pytest.fixture(scope="session")
def admin_token(client):
    # Obtain JWT for admin user
    data = {"username": "admin", "password": "adminpass"}
    response = client.post(
        "/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_token(client):
    # Register a test customer user
    payload = {"email": "cust@example.com", "password": "custpass", "role": "customer"}
    resp = client.post("/users/", json=payload)
    assert resp.status_code == 201
    # Login
    data = {"username": payload["email"], "password": payload["password"]}
    response = client.post(
        "/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
