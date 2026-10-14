"""
Sprint 2 (Kunal - Backend): Experience CRUD API endpoints.
Faculty can manage their professional experience records.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import SessionDep, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate, ExperienceResponse

router = APIRouter()


def _get_profile_or_404(session: Session, user_id: str) -> FacultyProfile:
    profile = (
        session.query(FacultyProfile).filter(FacultyProfile.user_id == user_id).first()
    )
    if not profile:
        raise HTTPException(status_code=400, detail="Faculty profile required.")
    return profile


@router.post(
    "/", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED
)
def create_experience(
    *,
    session: SessionDep,
    exp_in: ExperienceCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Add a new experience record to the current user's profile."""
    profile = _get_profile_or_404(session, current_user.id)
    db_exp = Experience(**exp_in.model_dump(), faculty_id=profile.id)
    session.add(db_exp)
    session.commit()
    session.refresh(db_exp)
    return db_exp


@router.get("/", response_model=List[ExperienceResponse])
@router.get("/me", response_model=List[ExperienceResponse])
def read_my_experience(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get all experience records for the currently logged-in user."""
    profile = _get_profile_or_404(session, current_user.id)
    return session.query(Experience).filter(Experience.faculty_id == profile.id).all()


@router.put("/{exp_id}", response_model=ExperienceResponse)
def update_experience(
    *,
    session: SessionDep,
    exp_id: str,
    exp_in: ExperienceCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update an existing experience record."""
    profile = _get_profile_or_404(session, current_user.id)
    record = (
        session.query(Experience)
        .filter(Experience.id == exp_id, Experience.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Experience record not found.")
    for field, value in exp_in.model_dump().items():
        setattr(record, field, value)
    session.commit()
    session.refresh(record)
    return record


@router.delete(
    "/{exp_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def delete_experience(
    *,
    session: SessionDep,
    exp_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete an experience record."""
    profile = _get_profile_or_404(session, current_user.id)
    record = (
        session.query(Experience)
        .filter(Experience.id == exp_id, Experience.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Experience record not found.")
    session.delete(record)
    session.commit()
