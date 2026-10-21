from pydantic import BaseModel
from datetime import date
from typing import Optional


class CertificationBase(BaseModel):
    name: str
    organization: str
    issue_date: date
    expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None


class CertificationInDB(CertificationBase):
    id: int
    faculty_profile_id: str

    class Config:
        from_attributes = True
