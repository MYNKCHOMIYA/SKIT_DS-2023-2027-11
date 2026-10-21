from pydantic import BaseModel
from app.models.student_guidance import GuidanceStatus


class StudentGuidanceBase(BaseModel):
    student_name: str
    project_title: str
    degree: str
    year: int
    status: GuidanceStatus


class StudentGuidanceCreate(StudentGuidanceBase):
    pass


class StudentGuidanceInDB(StudentGuidanceBase):
    id: int
    faculty_profile_id: str

    class Config:
        from_attributes = True
