"""
conftest.py — Shared pytest fixtures for GFPMS test suite.
DevOps / Sprint 1: Integration test environment setup.

Provides:
  - A SQLite in-memory test database (no PostgreSQL needed for unit tests).
  - An isolated DB session that rolls back after each test.
  - A FastAPI TestClient pre-wired to the in-memory DB.
  - Helper fixtures: registered_user, auth_headers.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base
from app.db.session import get_db

# ── In-memory SQLite engine for isolated, fast unit tests ────────────────────
SQLITE_URL = "sqlite://"   # pure in-memory; wiped after process exits

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # reuse single connection across threads
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once at the start of the test session."""
    import app.models  # Ensures all models are registered on Base.metadata
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """
    Yield an isolated DB session per test.
    Rolls back all changes after each test so tests don't pollute each other.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    FastAPI TestClient that uses the isolated in-memory DB session.
    Overrides the get_db dependency for the duration of each test.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # rollback handled by db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_user(client) -> dict:
    """Register a fresh faculty user and return the response JSON."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test_faculty@skit.ac.in", "password": "TestPass123!"},
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    return response.json()


@pytest.fixture()
def auth_headers(client, registered_user) -> dict:
    """Log in the test faculty user and return Bearer Authorization headers."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test_faculty@skit.ac.in",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
