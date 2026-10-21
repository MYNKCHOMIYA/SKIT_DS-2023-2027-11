import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class PatentStatus(str, enum.Enum):
    FILED = "FILED"
    PUBLISHED = "PUBLISHED"
    GRANTED = "GRANTED"
    REJECTED = "REJECTED"


class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    faculty_profile_id = Column(
        String, ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String, nullable=False)
    patent_number = Column(String, nullable=False, unique=True, index=True)
    filing_date = Column(Date, nullable=False)
    status = Column(Enum(PatentStatus), default=PatentStatus.FILED, nullable=False)
    inventors = Column(Text, nullable=False)
    link_url = Column(String, nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="patents")
