"""
test_integration_smoke.py — Sprint 1 Integration Smoke Tests
DevOps / Integration Engineer

Tests that the backend API is correctly wired end-to-end:
  - API root health check
  - Auth: register a new user
  - Auth: login with correct credentials -> receives JWT token
  - Auth: login with wrong credentials -> 401 Unauthorized
  - Auth: access protected /me endpoint with valid token
  - Auth: access protected /me endpoint without token -> 401

All tests use the in-memory SQLite DB provided by conftest.py fixtures.
Mark: [smoke] — these run in the CI integration-smoke job.
"""

import pytest


# ── [SMOKE] Health Check ──────────────────────────────────────────────────────

@pytest.mark.smoke
def test_root_health_check(client):
    """
    SMOKE: GET / should return 200 with a welcome message.
    Confirms the FastAPI app starts and is reachable.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


# ── [SMOKE] Auth: Register ───────────────────────────────────────────────────

@pytest.mark.smoke
def test_register_new_user(client):
    """
    SMOKE: POST /api/v1/auth/register should create a new faculty user.
    Confirms: response 201, email matches, role forced to 'faculty'.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "smoke_faculty@skit.ac.in", "password": "SmokePass99!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "smoke_faculty@skit.ac.in"
    assert data["role"] == "faculty"        # role must always default to faculty
    assert data["is_active"] is True
    assert "hashed_password" not in data    # never expose the hash


@pytest.mark.smoke
def test_register_duplicate_email_rejected(client, registered_user):
    """
    SMOKE: Registering with an already-used email must return 400.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test_faculty@skit.ac.in", "password": "AnotherPass!"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


# ── [SMOKE] Auth: Login ──────────────────────────────────────────────────────

@pytest.mark.smoke
def test_login_returns_jwt_token(client, registered_user):
    """
    SMOKE: POST /api/v1/auth/login with correct credentials returns a JWT.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_faculty@skit.ac.in", "password": "TestPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20    # sanity check: token is non-trivial


@pytest.mark.smoke
def test_login_wrong_password_rejected(client, registered_user):
    """
    SMOKE: Wrong password must return 401 Unauthorized.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_faculty@skit.ac.in", "password": "WrongPass!"},
    )
    assert response.status_code == 401


@pytest.mark.smoke
def test_login_nonexistent_user_rejected(client):
    """
    SMOKE: Login with an email that was never registered must return 401.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "ghost@skit.ac.in", "password": "SomePass!"},
    )
    assert response.status_code == 401


# ── [SMOKE] Auth: Protected Endpoint ─────────────────────────────────────────

@pytest.mark.smoke
def test_get_me_with_valid_token(client, auth_headers):
    """
    SMOKE: GET /api/v1/auth/me with a valid Bearer token returns current user.
    """
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_faculty@skit.ac.in"
    assert data["role"] == "faculty"


@pytest.mark.smoke
def test_get_me_without_token_returns_401(client):
    """
    SMOKE: GET /api/v1/auth/me without Authorization header must return 401.
    Confirms the endpoint is properly protected.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.smoke
def test_admin_user_list_blocked_for_faculty(client, auth_headers):
    """
    SMOKE: GET /api/v1/auth/users (admin-only) must return 403 for a faculty user.
    Confirms Role-Based Access Control is enforced from Sprint 1.
    """
    response = client.get("/api/v1/auth/users", headers=auth_headers)
    assert response.status_code == 403
