from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.teaching import Teaching
from app.schemas.teaching import TeachingCreate, TeachingInDB

router = APIRouter()


@router.post("/", response_model=TeachingInDB, status_code=status.HTTP_201_CREATED)
def create_teaching(
    teaching_in: TeachingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = (
        db.query(FacultyProfile)
        .filter(FacultyProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Faculty profile not found")

    teaching = Teaching(**teaching_in.model_dump(), faculty_profile_id=profile.id)
    db.add(teaching)
    db.commit()
    db.refresh(teaching)
    return teaching


@router.get("/", response_model=List[TeachingInDB])
def get_my_teaching(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = (
        db.query(FacultyProfile)
        .filter(FacultyProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        return []
    return profile.teaching


@router.delete("/{teaching_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teaching(
    teaching_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = (
        db.query(FacultyProfile)
        .filter(FacultyProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Faculty profile not found")

    teaching = (
        db.query(Teaching)
        .filter(Teaching.id == teaching_id, Teaching.faculty_profile_id == profile.id)
        .first()
    )
    if not teaching:
        raise HTTPException(status_code=404, detail="Teaching record not found")

    db.delete(teaching)
    db.commit()
    return {"ok": True}
