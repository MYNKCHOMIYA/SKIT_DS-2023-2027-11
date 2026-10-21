from pydantic import BaseModel
from typing import Optional


class FacultySearchResult(BaseModel):
    id: str
    user_id: str
    department: Optional[str] = None
    designation: Optional[str] = None
    total_publications: int
    total_projects: int

    # We use a flexible dictionary return to avoid crashing if
    # your exact MVP column names differ slightly from these!
    class Config:
        extra = "allow"
