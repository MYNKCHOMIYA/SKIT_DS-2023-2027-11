from pydantic import BaseModel


class TeachingBase(BaseModel):
    course_name: str
    subject_code: str
    semester: str
    academic_year: str
    credits: int


class TeachingCreate(TeachingBase):
    pass


class TeachingInDB(TeachingBase):
    id: int
    faculty_profile_id: str

    class Config:
        from_attributes = True
