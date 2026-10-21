from pydantic import BaseModel
from datetime import date
from typing import Optional


class WorkshopBase(BaseModel):
    event_name: str
    organizer: str
    event_date: date
    certificate_url: Optional[str] = None


class WorkshopCreate(WorkshopBase):
    pass


class WorkshopInDB(WorkshopBase):
    id: int
    faculty_profile_id: str

    class Config:
        from_attributes = True
