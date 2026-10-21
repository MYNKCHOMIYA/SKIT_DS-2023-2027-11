import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base


class GuidanceStatus(str, enum.Enum):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"


class StudentGuidance(Base):
    __tablename__ = "student_guidance"

    id = Column(Integer, primary_key=True, index=True)
    faculty_profile_id = Column(
        String, ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False
    )

    student_name = Column(String, nullable=False)
    project_title = Column(String, nullable=False)
    degree = Column(String, nullable=False)  # e.g., "B.Tech", "M.Tech", "Ph.D."
    year = Column(Integer, nullable=False)
    status = Column(
        Enum(GuidanceStatus), default=GuidanceStatus.ONGOING, nullable=False
    )

    faculty_profile = relationship("FacultyProfile", back_populates="student_guidance")
