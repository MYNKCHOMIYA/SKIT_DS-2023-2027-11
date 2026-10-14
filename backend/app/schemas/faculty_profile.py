"""
Sprint 2 (Kunal - Backend): Pydantic schemas for Faculty Profile CRUD operations.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class FacultyProfileBase(BaseModel):
    """Shared properties across create, read and update operations."""

    first_name: str = Field(
        ..., min_length=1, max_length=50, description="Faculty's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Faculty's last name"
    )
    designation: str = Field(
        ..., min_length=2, max_length=100, description="e.g., Assistant Professor, HOD"
    )
    department: Optional[str] = None
    skills: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

    employee_id: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    google_scholar: Optional[str] = None
    orcid: Optional[str] = None
    office_location: Optional[str] = None
    specialization: Optional[str] = None
    areas_of_interest: Optional[str] = None


class FacultyProfileCreate(FacultyProfileBase):
    """Properties to receive on Profile Creation.
    user_id is NOT exposed — extracted securely from the JWT token."""

    pass


class FacultyProfileUpdate(BaseModel):
    """Properties to receive on Profile Update — all fields optional."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    designation: Optional[str] = Field(default=None, min_length=2, max_length=100)
    department: Optional[str] = None
    skills: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

    employee_id: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    google_scholar: Optional[str] = None
    orcid: Optional[str] = None
    office_location: Optional[str] = None
    specialization: Optional[str] = None
    areas_of_interest: Optional[str] = None


class FacultyProfileResponse(FacultyProfileBase):
    """Properties returned to the React Frontend. Includes DB-generated IDs."""

    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)
