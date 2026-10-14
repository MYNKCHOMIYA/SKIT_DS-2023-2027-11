"""
Sprint 2 (Kunal - Backend): Education CRUD API endpoints.
Faculty can manage their academic qualification records.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import SessionDep, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.education import Education
from app.schemas.education import EducationCreate, EducationResponse

router = APIRouter()


def _get_profile_or_404(session: Session, user_id: str) -> FacultyProfile:
    """Helper: returns the faculty profile for the given user or raises 400."""
    profile = (
        session.query(FacultyProfile).filter(FacultyProfile.user_id == user_id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Faculty profile required. Please create your profile first.",
        )
    return profile


@router.post("/", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
def create_education(
    *,
    session: SessionDep,
    edu_in: EducationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Add a new education record to the current user's profile."""
    profile = _get_profile_or_404(session, current_user.id)
    db_edu = Education(**edu_in.model_dump(), faculty_id=profile.id)
    session.add(db_edu)
    session.commit()
    session.refresh(db_edu)
    return db_edu


@router.get("/", response_model=List[EducationResponse])
@router.get("/me", response_model=List[EducationResponse])
def read_my_education(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get all education records for the currently logged-in user."""
    profile = _get_profile_or_404(session, current_user.id)
    return session.query(Education).filter(Education.faculty_id == profile.id).all()


@router.put("/{edu_id}", response_model=EducationResponse)
def update_education(
    *,
    session: SessionDep,
    edu_id: str,
    edu_in: EducationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update an existing education record."""
    profile = _get_profile_or_404(session, current_user.id)
    record = (
        session.query(Education)
        .filter(Education.id == edu_id, Education.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Education record not found.")
    for field, value in edu_in.model_dump().items():
        setattr(record, field, value)
    session.commit()
    session.refresh(record)
    return record


@router.delete(
    "/{edu_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def delete_education(
    *,
    session: SessionDep,
    edu_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete an education record."""
    profile = _get_profile_or_404(session, current_user.id)
    record = (
        session.query(Education)
        .filter(Education.id == edu_id, Education.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Education record not found.")
    session.delete(record)
    session.commit()
