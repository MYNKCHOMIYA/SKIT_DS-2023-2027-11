from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    faculty_profile_id = Column(
        String, ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False
    )

    name = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    certificate_url = Column(String, nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="certifications")
