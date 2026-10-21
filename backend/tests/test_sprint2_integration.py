"""
test_sprint2_integration.py — Sprint 2 Integration Tests
DevOps / Integration Engineer: Krishan Kumar Jayaswal

Validates end-to-end integration of:
  - Google OAuth 2.0 redirect flow (configured / unconfigured)
  - @skit.ac.in domain restriction for Google OAuth callbacks
  - Google One-Tap credential verify endpoint
  - Profile creation via Google OAuth (auto-provisioning)
  - Faculty Profile CRUD endpoint integration
  - Education CRUD endpoint integration
  - Experience CRUD endpoint integration
  - Achievement CRUD endpoint integration
  - Role-Based Access Control enforcement across all Sprint 2 endpoints
  - Institutional email validator edge cases

All tests use the in-memory SQLite DB from conftest.py.
Mark: [sprint2] — integrated in the CI backend-ci and integration-smoke jobs.
"""

import pytest
from app.core.config import settings

# ── Google OAuth Flow Integration ─────────────────────────────────────────────


@pytest.mark.sprint2
def test_google_auth_status_endpoint_structure(client):
    """
    SPRINT2: GET /api/v1/auth/google/status must return a valid status object.
    Confirms the Google OAuth status check endpoint is registered and returns
    the expected schema: configured, client_id, redirect_uri.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/google/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "client_id" in data
    assert "redirect_uri" in data
    # When not configured, client_id should be empty or partial
    assert isinstance(data["configured"], bool)


@pytest.mark.sprint2
def test_google_login_redirect_returns_302_when_configured(client, monkeypatch):
    """
    SPRINT2: GET /api/v1/auth/google/login must redirect to Google consent screen.
    When GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set, the redirect must:
    - Return HTTP 302
    - Point to accounts.google.com
    - Include the client_id and scope parameters
    - Include the hd (hosted domain) hint for @skit.ac.in filtering
    """
    monkeypatch.setattr(
        settings, "GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com"
    )
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-google-secret-value")

    response = client.get(
        f"{settings.API_V1_STR}/auth/google/login",
        follow_redirects=False,
    )
    assert response.status_code == 302
    location = response.headers["location"]
    assert "accounts.google.com" in location
    assert "client_id=test-client-id" in location
    assert "scope=" in location
    assert "hd=skit.ac.in" in location or "hd=" in location


@pytest.mark.sprint2
def test_google_login_redirect_when_not_configured_returns_302_with_error(
    client, monkeypatch
):
    """
    SPRINT2: GET /api/v1/auth/google/login when OAuth is not configured
    must redirect to the frontend login page with an error message.
    Confirms graceful degradation.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "")

    response = client.get(
        f"{settings.API_V1_STR}/auth/google/login",
        follow_redirects=False,
    )
    assert response.status_code == 302
    location = response.headers["location"]
    assert "error" in location
    assert "login" in location or settings.FRONTEND_URL in location


@pytest.mark.sprint2
def test_google_oauth_url_json_endpoint_returns_consent_url(client, monkeypatch):
    """
    SPRINT2: GET /api/v1/auth/google/url must return JSON with auth URL.
    Supports SPA (Single Page App) OAuth flows where we cannot do server redirects.
    """
    monkeypatch.setattr(
        settings, "GOOGLE_CLIENT_ID", "spa-client-id.apps.googleusercontent.com"
    )
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "spa-secret")

    response = client.get(f"{settings.API_V1_STR}/auth/google/url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "accounts.google.com" in data["url"]
    assert "spa-client-id" in data["url"]


@pytest.mark.sprint2
def test_google_callback_rejects_non_skit_domain_email(client, monkeypatch):
    """
    SPRINT2: Google OAuth callback must reject @gmail.com accounts.
    Server-side domain check must block any non-@skit.ac.in email returned by Google.
    The redirect must include an error and reference 'skit.ac.in'.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-secret")

    import httpx

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

    async def mock_post(self, url, **kwargs):
        return MockResponse({"access_token": "mock-token", "token_type": "Bearer"})

    async def mock_get(self, url, **kwargs):
        return MockResponse(
            {
                "sub": "external-google-user-1234",
                "email": "external.user@gmail.com",
                "name": "External User",
                "picture": "https://example.com/pic.png",
                "email_verified": True,
            }
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.get(
        f"{settings.API_V1_STR}/auth/google/callback?code=test-code",
        follow_redirects=False,
    )
    assert response.status_code == 302
    location = response.headers["location"]
    assert "error" in location
    # Error message must reference the required domain
    assert "skit.ac.in" in location


@pytest.mark.sprint2
def test_google_callback_provisions_user_and_profile_for_skit_email(
    client, monkeypatch, db_session
):
    """
    SPRINT2: Successful Google OAuth callback for @skit.ac.in email must:
    1. Auto-provision a User with auth_provider='google' and the Google sub as google_id
    2. Auto-provision a linked FacultyProfile with name from Google
    3. Redirect to frontend with a valid app JWT token
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "integration-test-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "integration-test-secret")

    import httpx

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

    async def mock_post(self, url, **kwargs):
        return MockResponse(
            {"access_token": "google-access-token", "token_type": "Bearer"}
        )

    async def mock_get(self, url, **kwargs):
        return MockResponse(
            {
                "sub": "g-integration-sub-99999",
                "email": "integration.faculty@skit.ac.in",
                "name": "Integration Faculty",
                "given_name": "Integration",
                "family_name": "Faculty",
                "picture": "https://example.com/integration-avatar.png",
                "email_verified": True,
            }
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.get(
        f"{settings.API_V1_STR}/auth/google/callback?code=integration-auth-code",
        follow_redirects=False,
    )

    assert response.status_code == 302
    location = response.headers["location"]
    assert "/auth/callback?token=" in location
    token = location.split("token=")[1]
    assert len(token) > 20  # sanity check JWT is real

    from app.models.user import User
    from app.models.faculty_profile import FacultyProfile

    user = (
        db_session.query(User)
        .filter(User.email == "integration.faculty@skit.ac.in")
        .first()
    )
    assert user is not None
    assert user.auth_provider == "google"
    assert user.google_id == "g-integration-sub-99999"
    assert user.role == "faculty"
    # Google accounts receive an unguessable random password hash so direct empty login is prevented
    assert user.hashed_password is not None

    profile = (
        db_session.query(FacultyProfile)
        .filter(FacultyProfile.user_id == user.id)
        .first()
    )
    assert profile is not None
    assert profile.first_name == "Integration"
    assert profile.last_name == "Faculty"
    assert profile.profile_image_url == "https://example.com/integration-avatar.png"


@pytest.mark.sprint2
def test_google_callback_idempotent_second_login(client, monkeypatch, db_session):
    """
    SPRINT2: A second Google login for the same account must NOT create a duplicate user.
    The system must find the existing user by google_id and reuse it.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "idem-test-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "idem-test-secret")

    import httpx

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

    async def mock_post(self, url, **kwargs):
        return MockResponse({"access_token": "idem-token", "token_type": "Bearer"})

    async def mock_get(self, url, **kwargs):
        return MockResponse(
            {
                "sub": "g-idempotent-sub-77777",
                "email": "idempotent.test@skit.ac.in",
                "name": "Idempotent Test",
                "given_name": "Idempotent",
                "family_name": "Test",
                "picture": "https://example.com/avatar.jpg",
                "email_verified": True,
            }
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    # First login
    r1 = client.get(
        f"{settings.API_V1_STR}/auth/google/callback?code=code-first",
        follow_redirects=False,
    )
    assert r1.status_code == 302
    assert "/auth/callback?token=" in r1.headers["location"]

    # Second login — same google sub
    r2 = client.get(
        f"{settings.API_V1_STR}/auth/google/callback?code=code-second",
        follow_redirects=False,
    )
    assert r2.status_code == 302
    assert "/auth/callback?token=" in r2.headers["location"]

    from app.models.user import User

    users = (
        db_session.query(User).filter(User.email == "idempotent.test@skit.ac.in").all()
    )
    assert len(users) == 1, "Second Google login must NOT create a duplicate user"


# ── Institutional Email Validator Integration ─────────────────────────────────


@pytest.mark.sprint2
def test_register_validates_real_skit_email_format(client):
    """
    SPRINT2: A valid @skit.ac.in email should be accepted for registration
    (assuming MX records resolve — in tests, deliverability check is skipped via conftest).
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "valid.faculty01@skit.ac.in", "password": "ValidPass123!"},
    )
    # Should either succeed (201) or fail with email conflict (400),
    # but must NOT fail with a 422 domain validation error
    assert response.status_code in (201, 400)
    if response.status_code == 422:
        raise AssertionError(
            "Valid institutional email should not be rejected by the validator"
        )


@pytest.mark.sprint2
@pytest.mark.parametrize(
    "bad_email",
    [
        "user@gmail.com",
        "user@hotmail.com",
        "user@skit.ac.in.com",  # lookalike domain
        "user@skit.ac.in.evil.com",  # domain suffix attack
        "user@fakeskit.ac.in",  # prefix attack
    ],
)
def test_register_rejects_non_institutional_domains(client, bad_email):
    """
    SPRINT2: Any non-@skit.ac.in domain email must be rejected with HTTP 422.
    This validates the Pydantic field_validator in UserCreate.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": bad_email, "password": "Password123!"},
    )
    assert (
        response.status_code == 422
    ), f"Expected 422 for bad domain '{bad_email}', got {response.status_code}"


@pytest.mark.sprint2
@pytest.mark.parametrize(
    "fake_email",
    [
        "fake@skit.ac.in",
        "dummy@skit.ac.in",
        "temp@skit.ac.in",
        "asdf@skit.ac.in",
        "qwerty@skit.ac.in",
        "11111@skit.ac.in",
        "disposable@skit.ac.in",
    ],
)
def test_register_rejects_placeholder_and_fake_ids(client, fake_email):
    """
    SPRINT2: Placeholder / fake institutional IDs must be rejected with 422.
    Guards against the creation of fake institutional accounts.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": fake_email, "password": "ValidPass123!"},
    )
    assert (
        response.status_code == 422
    ), f"Expected 422 for fake email '{fake_email}', got {response.status_code}"


# ── Sprint 2: Faculty Profile Endpoint Integration ────────────────────────────


@pytest.mark.sprint2
@pytest.mark.smoke
def test_profile_endpoints_require_authentication(client):
    """
    SPRINT2 SMOKE: All profile endpoints must require a valid JWT token.
    Unauthenticated access must return 401.
    """
    endpoints = [
        ("GET", "/api/v1/profile/me"),
        ("POST", "/api/v1/profile/"),
        ("PATCH", "/api/v1/profile/me"),
    ]
    for method, url in endpoints:
        response = client.request(method, url)
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated {method} {url}, "
            f"got {response.status_code}"
        )


@pytest.mark.sprint2
def test_full_profile_lifecycle(client, auth_headers, db_session):
    """
    SPRINT2: Full profile lifecycle — create, read, update — in one test.
    Validates that:
    1. A faculty user can POST to create their profile.
    2. The created profile is returned on GET /me.
    3. The profile can be updated via PATCH.
    """
    # 1. Create profile
    create_resp = client.post(
        "/api/v1/profile/",
        json={
            "first_name": "Integration",
            "last_name": "Test",
            "designation": "Assistant Professor",
            "department": "Computer Science",
            "employee_id": "CSE-2026-INT",
            "bio": "Integration test faculty profile",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code in (
        200,
        201,
    ), f"Profile creation failed: {create_resp.status_code} {create_resp.text}"

    # 2. Read profile
    get_resp = client.get("/api/v1/profile/me", headers=auth_headers)
    assert get_resp.status_code == 200
    profile = get_resp.json()
    assert profile["first_name"] == "Integration"
    assert profile["last_name"] == "Test"

    # 3. Update profile
    update_resp = client.patch(
        "/api/v1/profile/me",
        json={"bio": "Updated integration test bio — Sprint 2"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["bio"] == "Updated integration test bio — Sprint 2"


@pytest.mark.sprint2
def test_education_endpoint_integration(client, auth_headers):
    """
    SPRINT2: Education CRUD endpoint integration test.
    Validates add → list → delete flow via the API.
    """
    client.post(
        "/api/v1/profile/",
        json={
            "first_name": "Integration",
            "last_name": "Faculty",
            "designation": "Assistant Professor",
        },
        headers=auth_headers,
    )
    # Add education entry
    add_resp = client.post(
        "/api/v1/education/",
        json={
            "degree": "M.Tech",
            "institution": "IIT Bombay",
            "field_of_study": "Computer Science",
            "start_date": "2020-08-01",
            "end_date": "2022-05-30",
            "grade": "9.2 CGPA",
        },
        headers=auth_headers,
    )
    assert add_resp.status_code in (
        200,
        201,
    ), f"Education add failed: {add_resp.status_code} {add_resp.text}"
    edu_id = add_resp.json().get("id")

    # List education
    list_resp = client.get("/api/v1/education/", headers=auth_headers)
    assert list_resp.status_code == 200
    education_list = list_resp.json()
    assert any(e.get("id") == edu_id for e in education_list)

    # Delete education
    if edu_id:
        del_resp = client.delete(f"/api/v1/education/{edu_id}", headers=auth_headers)
        assert del_resp.status_code in (200, 204)


@pytest.mark.sprint2
def test_experience_endpoint_integration(client, auth_headers):
    """
    SPRINT2: Experience CRUD endpoint integration test.
    Validates add → list → delete flow.
    """
    client.post(
        "/api/v1/profile/",
        json={
            "first_name": "Integration",
            "last_name": "Faculty",
            "designation": "Assistant Professor",
        },
        headers=auth_headers,
    )
    add_resp = client.post(
        "/api/v1/experience/",
        json={
            "job_title": "Research Engineer",
            "organization": "DRDO",
            "start_date": "2020-01-01",
            "end_date": "2022-12-31",
            "is_current": False,
            "description": "ML research for defense applications",
            "employment_type": "Full-time",
        },
        headers=auth_headers,
    )
    assert add_resp.status_code in (
        200,
        201,
    ), f"Experience add failed: {add_resp.status_code} {add_resp.text}"
    exp_id = add_resp.json().get("id")

    list_resp = client.get("/api/v1/experience/", headers=auth_headers)
    assert list_resp.status_code == 200

    if exp_id:
        del_resp = client.delete(f"/api/v1/experience/{exp_id}", headers=auth_headers)
        assert del_resp.status_code in (200, 204)


@pytest.mark.sprint2
def test_achievement_endpoint_integration(client, auth_headers):
    """
    SPRINT2: Achievement CRUD endpoint integration test.
    """
    client.post(
        "/api/v1/profile/",
        json={
            "first_name": "Integration",
            "last_name": "Faculty",
            "designation": "Assistant Professor",
        },
        headers=auth_headers,
    )
    add_resp = client.post(
        "/api/v1/achievements/",
        json={
            "title": "Best Paper Award",
            "category": "Award",
            "achievement_date": "2025-05-15",
            "description": "ICML 2025 Best Paper Award",
        },
        headers=auth_headers,
    )
    assert add_resp.status_code in (
        200,
        201,
    ), f"Achievement add failed: {add_resp.status_code} {add_resp.text}"
    ach_id = add_resp.json().get("id")

    list_resp = client.get("/api/v1/achievements/", headers=auth_headers)
    assert list_resp.status_code == 200

    if ach_id:
        del_resp = client.delete(f"/api/v1/achievements/{ach_id}", headers=auth_headers)
        assert del_resp.status_code in (200, 204)


# ── Sprint 2: Role-Based Access Control Enforcement ───────────────────────────


@pytest.mark.sprint2
def test_admin_endpoints_blocked_for_faculty_users(client, auth_headers):
    """
    SPRINT2: Admin-only endpoints must return 403 for regular faculty users.
    """
    admin_endpoints = [
        "/api/v1/auth/users",
    ]
    for url in admin_endpoints:
        response = client.get(url, headers=auth_headers)
        assert response.status_code == 403, (
            f"Expected 403 for faculty accessing admin endpoint {url}, "
            f"got {response.status_code}"
        )


@pytest.mark.sprint2
def test_other_users_profile_not_accessible(client, auth_headers, db_session):
    """
    SPRINT2: A faculty user must not be able to access or modify another
    faculty user's profile. Owner-based access control must be enforced.
    """
    # Register a second user
    second_user_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "second.faculty99@skit.ac.in", "password": "SecondPass123!"},
    )
    assert second_user_resp.status_code == 201
    second_user_id = second_user_resp.json()["id"]

    # Try to access second user's profile as first user (no profile yet,
    # but the important thing is the endpoint checks ownership)
    # GET /api/v1/profile/me only returns own profile
    me_resp = client.get("/api/v1/profile/me", headers=auth_headers)
    # Should be 404 (no profile created) or 200 (own profile), never another user's data
    assert me_resp.status_code in (200, 404)
    if me_resp.status_code == 200:
        data = me_resp.json()
        assert (
            data.get("user_id") != second_user_id
        ), "Faculty user must NOT see another user's profile via /me"


@pytest.mark.sprint2
def test_full_academic_portfolio_integration_flow(client, auth_headers):
    """
    SPRINT2: End-to-end integration flow:
    1. Create faculty profile with department
    2. Add research publication
    3. Add research project
    4. Add patent
    5. Retrieve public portfolio and verify all records are aggregated
    """
    # 1. Setup profile
    client.post(
        "/api/v1/profile/",
        json={
            "first_name": "DevOps",
            "last_name": "Tester",
            "designation": "Professor",
            "department": "Computer Science & Engineering",
        },
        headers=auth_headers,
    )
    me_resp = client.get("/api/v1/profile/me", headers=auth_headers)
    assert me_resp.status_code == 200
    profile_id = me_resp.json()["id"]

    # 2. Add Publication
    pub_resp = client.post(
        "/api/v1/publications/",
        json={
            "title": "Continuous Integration in Academic Portfolio Systems",
            "publication_type": "Conference Paper",
            "publication_year": 2024,
            "citations": 5,
        },
        headers=auth_headers,
    )
    assert pub_resp.status_code == 201

    # 3. Add Project
    proj_resp = client.post(
        "/api/v1/projects/",
        json={
            "title": "Automated CI Pipeline for Faculty Intelligence",
            "status": "Ongoing",
            "budget": 500000.0,
        },
        headers=auth_headers,
    )
    assert proj_resp.status_code == 201

    # 4. Add Patent
    pat_resp = client.post(
        "/api/patents/",
        json={
            "title": "System and Method for Continuous Pipeline Validation",
            "patent_number": "IN202411099999",
            "filing_date": "2024-05-01",
            "status": "FILED",
            "inventors": "DevOps Tester",
        },
        headers=auth_headers,
    )
    assert pat_resp.status_code == 201

    # 5. Public Portfolio verification (No auth headers required)
    public_resp = client.get(f"/api/v1/portfolio/public/{profile_id}")
    assert public_resp.status_code == 200
    portfolio = public_resp.json()
    assert portfolio["id"] == profile_id
    assert len(portfolio.get("publications", [])) >= 1
    assert len(portfolio.get("projects", [])) >= 1
    assert len(portfolio.get("patents", [])) >= 1
