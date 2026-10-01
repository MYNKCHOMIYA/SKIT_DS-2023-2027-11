from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class FacultyProfile(Base):
    """
    Sprint 1 (Mayank — AI/ML): Initial schema designed to support
    downstream analytical workloads. Fields chosen to allow statistical
    aggregation on publication counts, completeness scoring, and domain clustering.

    Key analytical considerations:
    - department_id kept as integer FK for easy GROUP BY queries
    - bio + skills stored as Text for NLP keyword extraction (Sprint 3+)
    - created_at / updated_at for time-series trend tracking
    """
    __tablename__ = "faculty_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)  # FK to User model (added Sprint 1)

    # Identity fields — also used as profile completeness metrics
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    designation = Column(String(100), nullable=False)
    department_id = Column(Integer, nullable=True)  # FK to Department table

    # Text fields — will be passed to NLP pipeline (TF-IDF, keyword extraction) in Sprint 3
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # comma-separated; parsed by analytics service

    # Timestamps for trend analytics (publication rate over time, activity tracking)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Sprint 2+: Relational fields (publications, education, etc.) will be added here.
    # Example planned metrics:
    #   - publications.count()         → paper count per year
    #   - publications.citations.sum() → h-index simulation
    #   - achievements.count()         → profile completeness boost
