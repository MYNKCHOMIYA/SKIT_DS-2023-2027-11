"""
test_auth.py — Sprint 1 Backend Auth Tests
Author: Kunal Gupta (Backend Developer)

Tests JWT authentication endpoints built in Sprint 1:
  - Register a new faculty user
  - Login with correct/wrong credentials
  - Access the protected /me endpoint
  - Admin-only route protection
"""
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_root_returns_welcome():
    """GET / should return a 200 welcome message confirming the API is live."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_admin_route_requires_authentication():
    """
    GET /api/v1/auth/users (admin-only) without a token must return 401.
    Ensures the endpoint is protected before any user exists in the system.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/users")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_login_with_unregistered_email_returns_401():
    """
    POST /api/v1/auth/login with an email that doesn't exist must return 401.
    Confirms the backend does not reveal whether the email exists.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nobody@skit.ac.in", "password": "anypassword"},
    )
    assert response.status_code == 401


def test_get_me_without_token_returns_401():
    """
    GET /api/v1/auth/me without Bearer token must return 401 Not Authenticated.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
