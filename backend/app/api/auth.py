from datetime import timedelta
import secrets
from typing import Any, List
from urllib.parse import quote, urlencode
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, get_current_active_user, get_current_admin
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.models.department import Department
from app.models.faculty_profile import FacultyProfile
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserAdminResponse,
    UserRoleUpdate,
    GoogleVerifyRequest,
    GoogleAuthStatusResponse,
)
from app.schemas.token import Token

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user_in: UserCreate, session: SessionDep) -> Any:
    """
    Register a new user. Role is always set to 'faculty' regardless of input.
    Roles can only be elevated by an administrator after registration.
    """
    # Check if user already exists
    user = session.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Always force role to 'faculty' — no self-elevation allowed
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role="faculty",
        department_id=None,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login_access_token(
    session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Verify user exists
    user = session.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not user.hashed_password or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user is active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Generate JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user. This endpoint acts as a test to verify the JWT token works.
    """
    return current_user


@router.get("/users", response_model=List[UserAdminResponse])
def read_all_users(
    session: SessionDep,
    current_admin: User = Depends(get_current_admin),
):
    """
    ADMIN ONLY: Retrieve a list of all registered users with their department info.
    """
    users = session.query(User).all()
    result = []
    for u in users:
        dept_name = u.department.name if u.department else None
        result.append(
            UserAdminResponse(
                id=u.id,
                email=u.email,
                is_active=u.is_active,
                role=u.role,
                department_id=u.department_id,
                department_name=dept_name,
            )
        )
    return result


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    session: SessionDep,
    current_admin: User = Depends(get_current_admin),
) -> Any:
    """
    ADMIN ONLY: Update a user's role and department assignment.
    - Setting role to 'hod' requires a department_id.
    - Setting role to 'faculty' clears their department assignment.
    """
    target_user = session.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent admin from demoting themselves
    if target_user.id == current_admin.id:
        raise HTTPException(
            status_code=400, detail="Administrators cannot change their own role"
        )

    # Validate department exists when assigning HOD
    if role_update.role == "hod" and role_update.department_id:
        dept = (
            session.query(Department)
            .filter(Department.id == role_update.department_id)
            .first()
        )
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")

    target_user.role = role_update.role
    # Clear department if demoting to faculty, otherwise assign the department
    if role_update.role == "faculty":
        target_user.department_id = None
    else:
        target_user.department_id = role_update.department_id

    session.commit()
    session.refresh(target_user)
    return target_user


@router.get("/departments", response_model=List[dict])
def list_departments(
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    List all departments. Used by admin UI for the role-assignment dropdown.
    """
    departments = session.query(Department).all()
    return [{"id": d.id, "name": d.name, "code": d.code} for d in departments]


# ─────────────────────────────────────────────────────────────────────────────
# Google OAuth 2.0 Helpers & Endpoints
# ─────────────────────────────────────────────────────────────────────────────


def get_or_create_google_user(
    session: SessionDep,
    google_id: str,
    email: str,
    name: str | None = None,
    given_name: str | None = None,
    family_name: str | None = None,
    picture: str | None = None,
) -> User:
    """
    Finds or provisions a User and FacultyProfile for a verified Google account.
    If the email already exists under local auth, safely links google_id to that account.
    """
    # 1. Match by google_id
    user = session.query(User).filter(User.google_id == google_id).first()

    # 2. Match by email if not found by google_id
    if not user:
        user = session.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id
        else:
            # Create a brand new user via Google Sign-In
            random_pwd = secrets.token_urlsafe(32)
            user = User(
                email=email,
                hashed_password=get_password_hash(random_pwd),
                auth_provider="google",
                google_id=google_id,
                role="faculty",
                is_active=True,
            )
            session.add(user)
            session.flush()

    # 3. Provision or enrich FacultyProfile
    if not user.profile:
        first = given_name or (name.split()[0] if name and name.strip() else "Faculty")
        last = family_name or (
            " ".join(name.split()[1:]) if name and len(name.split()) > 1 else "Member"
        )
        profile = FacultyProfile(
            user_id=user.id,
            first_name=first,
            last_name=last,
            designation="Faculty",
            profile_image_url=picture,
        )
        session.add(profile)
    elif picture and not user.profile.profile_image_url:
        user.profile.profile_image_url = picture

    session.commit()
    session.refresh(user)
    return user


@router.get("/google/status", response_model=GoogleAuthStatusResponse)
def get_google_auth_status() -> Any:
    """
    Check if Google OAuth is configured on this backend instance.
    """
    return GoogleAuthStatusResponse(
        configured=bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        client_id=settings.GOOGLE_CLIENT_ID,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


@router.get("/google/url")
def get_google_auth_url() -> Any:
    """
    Generate Google OAuth authorization URL for frontend redirection.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured on the server. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend .env",
        )
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "hd": settings.ALLOWED_COLLEGE_DOMAIN,
    }
    return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"}


@router.get("/google/login")
def google_login_redirect() -> Any:
    """
    Redirect the user's browser directly to Google's OAuth consent screen.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        error_msg = quote(
            "Google OAuth is not configured on the server. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend .env"
        )
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={error_msg}",
            status_code=status.HTTP_302_FOUND,
        )
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "hd": settings.ALLOWED_COLLEGE_DOMAIN,
    }
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/google/callback")
async def google_callback(
    session: SessionDep,
    code: str | None = None,
    error: str | None = None,
) -> Any:
    """
    Handles Google OAuth redirect with authorization code, exchanges it for tokens,
    provisions or fetches the user, and redirects to frontend with an application JWT.
    """
    if error:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={quote(error)}",
            status_code=status.HTTP_302_FOUND,
        )

    if not code:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={quote('Missing authorization code from Google')}",
            status_code=status.HTTP_302_FOUND,
        )

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={quote('Google OAuth credentials not configured on backend')}",
            status_code=status.HTTP_302_FOUND,
        )

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(token_url, data=token_data)
            if token_resp.status_code != 200:
                err_detail = token_resp.json().get(
                    "error_description", "Failed to exchange token with Google"
                )
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error={quote(err_detail)}",
                    status_code=status.HTTP_302_FOUND,
                )
            tokens = token_resp.json()
            access_token = tokens.get("access_token")

            userinfo_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if userinfo_resp.status_code != 200:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error={quote('Failed to fetch user profile from Google')}",
                    status_code=status.HTTP_302_FOUND,
                )
            userinfo = userinfo_resp.json()

    except Exception as e:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={quote(f'Google OAuth network error: {str(e)}')}",
            status_code=status.HTTP_302_FOUND,
        )

    email = userinfo.get("email")
    google_id = userinfo.get("sub")
    if not email or not google_id:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={quote('Google account is missing required email or user ID')}",
            status_code=status.HTTP_302_FOUND,
        )

    # Domain restriction check: strictly require @skit.ac.in
    allowed = settings.ALLOWED_COLLEGE_DOMAIN.lower()
    if not email.lower().endswith(f"@{allowed}"):
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={quote('Access denied: Only official @' + allowed + ' Google accounts are allowed.')}",
            status_code=status.HTTP_302_FOUND,
        )

    user = get_or_create_google_user(
        session=session,
        google_id=google_id,
        email=email,
        name=userinfo.get("name"),
        given_name=userinfo.get("given_name"),
        family_name=userinfo.get("family_name"),
        picture=userinfo.get("picture"),
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    app_jwt = create_access_token(subject=user.id, expires_delta=access_token_expires)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/auth/callback?token={app_jwt}",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/google/verify", response_model=Token)
async def google_verify_credential(
    payload: GoogleVerifyRequest,
    session: SessionDep,
) -> Any:
    """
    Verifies a Google ID credential token directly (e.g. from Google One-Tap or GSI SDK)
    and returns an application access token.
    """
    token_info_url = (
        f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.credential}"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(token_info_url)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Google credential token",
                )
            userinfo = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to Google auth service: {str(e)}",
        )

    # Validate audience if client ID is set
    if settings.GOOGLE_CLIENT_ID and userinfo.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token audience does not match configured Google Client ID",
        )

    email = userinfo.get("email")
    google_id = userinfo.get("sub")
    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google credential does not contain email or subject ID",
        )

    # Domain restriction check: strictly require @skit.ac.in
    allowed = settings.ALLOWED_COLLEGE_DOMAIN.lower()
    if not email.lower().endswith(f"@{allowed}"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Only official @{allowed} accounts are allowed.",
        )

    user = get_or_create_google_user(
        session=session,
        google_id=google_id,
        email=email,
        name=userinfo.get("name"),
        given_name=userinfo.get("given_name"),
        family_name=userinfo.get("family_name"),
        picture=userinfo.get("picture"),
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    app_jwt = create_access_token(subject=user.id, expires_delta=access_token_expires)

    return {
        "access_token": app_jwt,
        "token_type": "bearer",
    }
