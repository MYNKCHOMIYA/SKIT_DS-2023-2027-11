from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    faculty_profile_id = Column(
        String, ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False
    )

    event_name = Column(String, nullable=False)
    organizer = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    certificate_url = Column(String, nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="workshops")
