from app.models.base import Base
from app.models.department import Department
from app.models.faculty_profile import FacultyProfile
from app.models.user import User
from app.models.education import Education
from app.models.experience import Experience
from app.models.achievement import Achievement

__all__ = [
    "Base",
    "Department",
    "FacultyProfile",
    "User",
    "Education",
    "Experience",
    "Achievement",
]
