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

@pytest.fixture(scope="module")
def client():
    """
    TestClient–fixture for å sende HTTP-forespørsler til FastAPI-appen.
    Scope 'module' slik at vi gjenbruker client for alle tester i hver fil.
    """
    with TestClient(fastapi_app) as test_client:
        yield test_client

# Ensure each test runs with a fresh database
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
