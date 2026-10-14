"""
Sprint 2 (Kunal - Backend): Faculty Profile CRUD API endpoints.
Implements secure create, read and update operations on faculty profiles.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_active_user, get_current_admin
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.schemas.faculty_profile import (
    FacultyProfileCreate,
    FacultyProfileUpdate,
    FacultyProfileResponse,
)

router = APIRouter()


@router.post(
    "/", response_model=FacultyProfileResponse, status_code=status.HTTP_201_CREATED
)
def create_profile(
    *,
    session: SessionDep,
    profile_in: FacultyProfileCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new faculty profile for the currently logged-in user.
    Each user can only have one profile (enforced via unique constraint).
    """
    existing_profile = (
        session.query(FacultyProfile)
        .filter(FacultyProfile.user_id == current_user.id)
        .first()
    )
    if existing_profile:
        raise HTTPException(
            status_code=400, detail="A profile already exists for this user."
        )

    db_profile = FacultyProfile(**profile_in.model_dump(), user_id=current_user.id)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.get("/me", response_model=FacultyProfileResponse)
def read_profile_me(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get the profile of the currently logged-in user."""
    profile = (
        session.query(FacultyProfile)
        .filter(FacultyProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found. Please create one first."
        )
    return profile


@router.patch("/me", response_model=FacultyProfileResponse)
def update_profile_me(
    *,
    session: SessionDep,
    profile_in: FacultyProfileUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update the profile of the currently logged-in user (partial update)."""
    profile = (
        session.query(FacultyProfile)
        .filter(FacultyProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    session.commit()
    session.refresh(profile)
    return profile


@router.get("/all", response_model=List[FacultyProfileResponse])
def read_all_profiles(
    session: SessionDep,
    current_admin: User = Depends(get_current_admin),
) -> Any:
    """ADMIN ONLY: Retrieve all faculty profiles."""
    return session.query(FacultyProfile).all()
