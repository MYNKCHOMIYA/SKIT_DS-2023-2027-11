from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.patent import PatentStatus


class PatentBase(BaseModel):
    title: str
    patent_number: str
    filing_date: date
    status: PatentStatus
    inventors: str
    link_url: Optional[str] = None


class PatentCreate(PatentBase):
    pass


class PatentUpdate(BaseModel):
    title: Optional[str] = None
    patent_number: Optional[str] = None
    filing_date: Optional[date] = None
    status: Optional[PatentStatus] = None
    inventors: Optional[str] = None
    link_url: Optional[str] = None


class PatentInDB(PatentBase):
    id: int
    faculty_profile_id: str

    class Config:
        from_attributes = True
