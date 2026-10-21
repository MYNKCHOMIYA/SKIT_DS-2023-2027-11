from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.student_guidance import StudentGuidance
from app.schemas.student_guidance import StudentGuidanceCreate, StudentGuidanceInDB

router = APIRouter()


@router.post(
    "/", response_model=StudentGuidanceInDB, status_code=status.HTTP_201_CREATED
)
def create_student_guidance(
    guidance_in: StudentGuidanceCreate,
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

    guidance = StudentGuidance(
        **guidance_in.model_dump(), faculty_profile_id=profile.id
    )
    db.add(guidance)
    db.commit()
    db.refresh(guidance)
    return guidance


@router.get("/", response_model=List[StudentGuidanceInDB])
def get_my_student_guidance(
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
    return profile.student_guidance


@router.delete("/{guidance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_guidance(
    guidance_id: int,
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

    guidance = (
        db.query(StudentGuidance)
        .filter(
            StudentGuidance.id == guidance_id,
            StudentGuidance.faculty_profile_id == profile.id,
        )
        .first()
    )
    if not guidance:
        raise HTTPException(status_code=404, detail="Student guidance record not found")

    db.delete(guidance)
    db.commit()
    return {"ok": True}
