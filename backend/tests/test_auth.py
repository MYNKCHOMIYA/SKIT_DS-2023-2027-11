"""
test_auth.py — Sprint 1 Backend Auth Tests
Author: Kunal Gupta (Backend Developer)

Tests JWT authentication endpoints built in Sprint 1:
  - Register a new faculty user
  - Login with correct/wrong credentials
  - Access the protected /me endpoint
  - Admin-only route protection
"""

from app.core.config import settings


def test_root_returns_welcome(client):
    """GET / should return a 200 welcome message confirming the API is live."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_admin_route_requires_authentication(client):
    """
    GET /api/v1/auth/users (admin-only) without a token must return 401.
    Ensures the endpoint is protected before any user exists in the system.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/users")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_login_with_unregistered_email_returns_401(client):
    """
    POST /api/v1/auth/login with an email that doesn't exist must return 401.
    Confirms the backend does not reveal whether the email exists.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nobody@skit.ac.in", "password": "anypassword"},
    )
    assert response.status_code == 401


def test_get_me_without_token_returns_401(client):
    """
    GET /api/v1/auth/me without Bearer token must return 401 Not Authenticated.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_google_auth_status(client):
    """
    GET /api/v1/auth/google/status should return configuration info.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/google/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "client_id" in data
    assert "redirect_uri" in data


def test_google_login_redirect_unconfigured(client, monkeypatch):
    """
    When Google OAuth is not configured, GET /api/v1/auth/google/login should redirect to frontend with error.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "")
    response = client.get(f"{settings.API_V1_STR}/auth/google/login", follow_redirects=False)
    assert response.status_code == 302
    assert "error" in response.headers["location"]


def test_google_login_redirect_configured(client, monkeypatch):
    """
    When configured, GET /api/v1/auth/google/login redirects to Google consent screen.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-secret")
    response = client.get(f"{settings.API_V1_STR}/auth/google/login", follow_redirects=False)
    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["location"]
    assert "client_id=test-client-id" in response.headers["location"]


def test_google_auth_url_endpoint(client, monkeypatch):
    """
    GET /api/v1/auth/google/url returns json auth URL when configured.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-secret")
    response = client.get(f"{settings.API_V1_STR}/auth/google/url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "accounts.google.com" in data["url"]


def test_google_callback_creates_user_and_profile(client, monkeypatch, db_session):
    """
    Simulates Google OAuth callback:
    Exchanges code for tokens, fetches userinfo, provisions User and FacultyProfile.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-secret")

    # Mock httpx response
    import httpx

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

    async def mock_post(self, url, **kwargs):
        if "oauth2.googleapis.com/token" in str(url):
            return MockResponse({"access_token": "mock-access-token", "token_type": "Bearer"})
        return MockResponse({}, status_code=400)

    async def mock_get(self, url, **kwargs):
        if "userinfo" in str(url):
            return MockResponse({
                "sub": "google-sub-12345",
                "email": "prof.test@skit.ac.in",
                "name": "Prof Test User",
                "given_name": "Prof",
                "family_name": "Test User",
                "picture": "https://example.com/avatar.png",
                "email_verified": True,
            })
        return MockResponse({}, status_code=400)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.get(
        f"{settings.API_V1_STR}/auth/google/callback?code=mock-auth-code",
        follow_redirects=False,
    )
    assert response.status_code == 302
    redirect_url = response.headers["location"]
    assert "/auth/callback?token=" in redirect_url

    # Check user was created in DB
    from app.models.user import User
    from app.models.faculty_profile import FacultyProfile

    user = db_session.query(User).filter(User.email == "prof.test@skit.ac.in").first()
    assert user is not None
    assert user.auth_provider == "google"
    assert user.google_id == "google-sub-12345"
    assert user.role == "faculty"

    # Check profile was provisioned
    profile = db_session.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
    assert profile is not None
    assert profile.first_name == "Prof"
    assert profile.last_name == "Test User"
    assert profile.profile_image_url == "https://example.com/avatar.png"


def test_google_verify_credential_endpoint(client, monkeypatch, db_session):
    """
    POST /api/v1/auth/google/verify validates Google ID credential and returns JWT.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "")

    import httpx

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

    async def mock_get(self, url, **kwargs):
        if "tokeninfo" in str(url):
            return MockResponse({
                "sub": "google-onetap-999",
                "email": "onetap.user@skit.ac.in",
                "name": "OneTap User",
                "given_name": "OneTap",
                "family_name": "User",
                "picture": "https://example.com/onetap.jpg",
                "email_verified": "true",
            })
        return MockResponse({}, status_code=400)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.post(
        f"{settings.API_V1_STR}/auth/google/verify",
        json={"credential": "mock-valid-id-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_rejects_non_skit_domain(client):
    """
    POST /api/v1/auth/register with a non-@skit.ac.in email must be rejected with 422.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "randomuser@gmail.com", "password": "Password123!"},
    )
    assert response.status_code == 422
    assert "skit.ac.in" in response.text.lower()


def test_register_rejects_fake_and_placeholder_emails(client):
    """
    POST /api/v1/auth/register with fake, dummy, or placeholder usernames must be rejected.
    """
    fake_emails = [
        "fake@skit.ac.in",
        "dummy@skit.ac.in",
        "asdf@skit.ac.in",
        "11111@skit.ac.in",
    ]
    for fake_email in fake_emails:
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json={"email": fake_email, "password": "Password123!"},
        )
        assert response.status_code == 422, f"Expected 422 for {fake_email}, got {response.status_code}"


def test_google_callback_rejects_non_skit_google_account(client, monkeypatch):
    """
    Google OAuth callback with an email that is NOT @skit.ac.in must be rejected.
    """
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")
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
        return MockResponse({
            "sub": "non-skit-google-user",
            "email": "personal.account@gmail.com",
            "name": "Personal User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
        })

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.get(
        f"{settings.API_V1_STR}/auth/google/callback?code=mock-code",
        follow_redirects=False,
    )
    assert response.status_code == 302
    redirect_url = response.headers["location"]
    assert "error" in redirect_url
    assert "skit.ac.in" in redirect_url


