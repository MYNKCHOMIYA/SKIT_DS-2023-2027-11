from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import SessionDep, get_current_active_user
from app.models.user import User
from app.models.faculty_profile import FacultyProfile
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()


def get_current_faculty_profile(session: Session, user_id: str) -> FacultyProfile:
    profile = (
        session.query(FacultyProfile).filter(FacultyProfile.user_id == user_id).first()
    )
    if not profile:
        raise HTTPException(status_code=400, detail="Faculty profile required.")
    return profile


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    session: SessionDep,
    proj_in: ProjectCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    profile = get_current_faculty_profile(session, current_user.id)
    db_proj = Project(**proj_in.model_dump(), faculty_id=profile.id)
    session.add(db_proj)
    session.commit()
    session.refresh(db_proj)
    return db_proj


@router.get("/me", response_model=List[ProjectResponse])
def read_my_projects(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    profile = get_current_faculty_profile(session, current_user.id)
    return session.query(Project).filter(Project.faculty_id == profile.id).all()


@router.put("/{id}", response_model=ProjectResponse)
def update_project(
    *,
    session: SessionDep,
    id: str,
    proj_in: ProjectUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    profile = get_current_faculty_profile(session, current_user.id)
    record = (
        session.query(Project)
        .filter(Project.id == id, Project.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = proj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_project(
    *,
    session: SessionDep,
    id: str,
    current_user: User = Depends(get_current_active_user)
) -> None:
    profile = get_current_faculty_profile(session, current_user.id)
    record = (
        session.query(Project)
        .filter(Project.id == id, Project.faculty_id == profile.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(record)
    session.commit()
