from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.workshop import Workshop
from app.schemas.workshop import WorkshopCreate, WorkshopInDB

router = APIRouter()


@router.post("/", response_model=WorkshopInDB, status_code=status.HTTP_201_CREATED)
def create_workshop(
    workshop_in: WorkshopCreate,
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

    workshop = Workshop(**workshop_in.model_dump(), faculty_profile_id=profile.id)
    db.add(workshop)
    db.commit()
    db.refresh(workshop)
    return workshop


@router.get("/", response_model=List[WorkshopInDB])
def get_my_workshops(
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
    return profile.workshops


@router.delete("/{workshop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workshop(
    workshop_id: int,
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

    workshop = (
        db.query(Workshop)
        .filter(Workshop.id == workshop_id, Workshop.faculty_profile_id == profile.id)
        .first()
    )
    if not workshop:
        raise HTTPException(status_code=404, detail="Workshop record not found")

    db.delete(workshop)
    db.commit()
    return {"ok": True}
