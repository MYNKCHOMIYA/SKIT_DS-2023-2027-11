from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class ProjectBase(BaseModel):
    title: str
    funding_agency: Optional[str] = None
    budget: Optional[float] = None
    status: str = "Ongoing"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    # Add these inside your Pydantic Base schema
    team_members: Optional[str] = None
    project_documents_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    funding_agency: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    team_members: Optional[str] = None
    project_documents_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    faculty_id: str
    model_config = ConfigDict(from_attributes=True)
