from pydantic import BaseModel, EmailStr, field_validator
from app.core.validators import validate_institutional_email


class UserCreate(BaseModel):
    """Schema for user registration — role is always forced to 'faculty' by the backend."""

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_domain_and_authenticity(cls, v: str) -> str:
        return validate_institutional_email(str(v))


class UserResponse(BaseModel):
    """Public-safe user response schema."""

    id: str
    email: EmailStr
    is_active: bool
    role: str
    auth_provider: str = "local"

    class Config:
        from_attributes = True


class UserAdminResponse(BaseModel):
    """Extended user response for Admin-only endpoints."""

    id: str
    email: EmailStr
    is_active: bool
    role: str
    auth_provider: str = "local"
    department_id: str | None = None
    department_name: str | None = None

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Schema for admin role-assignment endpoint."""

    role: str  # admin | hod | faculty
    department_id: str | None = None


class GoogleVerifyRequest(BaseModel):
    """Schema for direct Google token verification (e.g. One-Tap or Google Sign-In SDK)."""

    credential: str


class GoogleAuthStatusResponse(BaseModel):
    """Schema for checking backend Google OAuth status."""

    configured: bool
    client_id: str
    redirect_uri: str
