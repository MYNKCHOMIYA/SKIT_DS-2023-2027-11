from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.certification import Certification
from app.schemas.certification import (
    CertificationCreate,
    CertificationInDB,
)

router = APIRouter()


@router.post("/", response_model=CertificationInDB, status_code=status.HTTP_201_CREATED)
def create_certification(
    cert_in: CertificationCreate,
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

    cert = Certification(**cert_in.model_dump(), faculty_profile_id=profile.id)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.get("/", response_model=List[CertificationInDB])
def get_my_certifications(
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
    return profile.certifications


@router.delete("/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(
    cert_id: int,
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

    cert = (
        db.query(Certification)
        .filter(
            Certification.id == cert_id, Certification.faculty_profile_id == profile.id
        )
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    db.delete(cert)
    db.commit()
    return {"ok": True}
