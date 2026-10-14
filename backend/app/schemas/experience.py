"""
Sprint 2 (Kunal - Backend): Pydantic schemas for Experience CRUD operations.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class ExperienceBase(BaseModel):
    job_title: str
    organization: str
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    employment_type: Optional[str] = None  # Full-time, Part-time, Contractual


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: str
    faculty_id: str

    model_config = ConfigDict(from_attributes=True)
