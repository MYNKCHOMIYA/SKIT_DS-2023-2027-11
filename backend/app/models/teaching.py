from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Teaching(Base):
    __tablename__ = "teaching"

    id = Column(Integer, primary_key=True, index=True)
    # Using String for the foreign key to match your UUID setup!
    faculty_profile_id = Column(
        String, ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False
    )

    course_name = Column(String, nullable=False)
    subject_code = Column(String, nullable=False)
    semester = Column(String, nullable=False)  # e.g., "Fall", "Spring", "Even", "Odd"
    academic_year = Column(String, nullable=False)  # e.g., "2025-2026"
    credits = Column(Integer, nullable=False)

    faculty_profile = relationship("FacultyProfile", back_populates="teaching")
