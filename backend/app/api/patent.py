from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.patent import Patent
from app.schemas.patent import PatentCreate, PatentInDB

router = APIRouter()


@router.post("/", response_model=PatentInDB, status_code=status.HTTP_201_CREATED)
def create_patent(
    patent_in: PatentCreate,
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

    patent = Patent(**patent_in.model_dump(), faculty_profile_id=profile.id)
    db.add(patent)
    db.commit()
    db.refresh(patent)
    return patent


@router.get("/", response_model=List[PatentInDB])
def get_my_patents(
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
    return profile.patents


@router.delete("/{patent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patent(
    patent_id: int,
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

    patent = (
        db.query(Patent)
        .filter(Patent.id == patent_id, Patent.faculty_profile_id == profile.id)
        .first()
    )
    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")

    db.delete(patent)
    db.commit()
    return {"ok": True}
