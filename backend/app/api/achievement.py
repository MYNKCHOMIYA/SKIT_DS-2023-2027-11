"""
Sprint 2 (Kunal - Backend): Achievement CRUD API endpoints.
Faculty can manage their awards, recognitions, and memberships.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import SessionDep, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreate, AchievementResponse

router = APIRouter()


def _get_profile_or_404(session: Session, user_id: str) -> FacultyProfile:
    profile = (
        session.query(FacultyProfile).filter(FacultyProfile.user_id == user_id).first()
    )
    if not profile:
        raise HTTPException(status_code=400, detail="Faculty profile required.")
    return profile


@router.post(
    "/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED
)
def create_achievement(
    *,
    session: SessionDep,
    ach_in: AchievementCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Add a new achievement record."""
    profile = _get_profile_or_404(session, current_user.id)
    db_ach = Achievement(**ach_in.model_dump(), faculty_id=profile.id)
    session.add(db_ach)
    session.commit()
    session.refresh(db_ach)
    return db_ach


@router.get("/", response_model=List[AchievementResponse])
@router.get("/me", response_model=List[AchievementResponse])
def read_my_achievements(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get all achievements for the currently logged-in user."""
    profile = _get_profile_or_404(session, current_user.id)
    return session.query(Achievement).filter(Achievement.faculty_id == profile.id).all()


@router.put("/{ach_id}", response_model=AchievementResponse)
def update_achievement(
    *,
    session: SessionDep,
    ach_id: str,
    ach_in: AchievementCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update an existing achievement record."""
    profile = _get_profile_or_404(session, current_user.id)
    record = (
        session.query(Achievement)
        .filter(Achievement.id == ach_id, Achievement.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Achievement not found.")
    for field, value in ach_in.model_dump().items():
        setattr(record, field, value)
    session.commit()
    session.refresh(record)
    return record


@router.delete(
    "/{ach_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def delete_achievement(
    *,
    session: SessionDep,
    ach_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete an achievement record."""
    profile = _get_profile_or_404(session, current_user.id)
    record = (
        session.query(Achievement)
        .filter(Achievement.id == ach_id, Achievement.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Achievement not found.")
    session.delete(record)
    session.commit()
