from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class FacultyProfile(Base):
    """
    Core profile model tailored for analytical normalization.
    """
    __tablename__ = "faculty_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False) # FK to User model
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    designation = Column(String(100), nullable=False)
    department_id = Column(Integer, nullable=False) # FK to Department
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Future Relationships (Sprint 3)
    # education = relationship("Education", back_populates="faculty")
    # publications = relationship("Publication", back_populates="faculty")
