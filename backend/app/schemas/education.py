"""
Sprint 2 (Kunal - Backend): Pydantic schemas for Education CRUD operations.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class EducationBase(BaseModel):
    degree: str  # e.g., Ph.D., M.Tech, B.Tech
    institution: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    grade: Optional[str] = None  # CGPA or Percentage


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: str
    faculty_id: str

    model_config = ConfigDict(from_attributes=True)
