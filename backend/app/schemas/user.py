from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration — role is always forced to 'faculty' by the backend."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public-safe user response schema."""

    id: str
    email: EmailStr
    is_active: bool
    role: str

    class Config:
        from_attributes = True


class UserAdminResponse(BaseModel):
    """Extended user response for Admin-only endpoints."""

    id: str
    email: EmailStr
    is_active: bool
    role: str
    department_id: str | None = None
    department_name: str | None = None

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Schema for admin role-assignment endpoint."""

    role: str  # admin | hod | faculty
    department_id: str | None = None
