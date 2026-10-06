from sqlalchemy import String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import uuid
from datetime import datetime


class FacultyProfile(Base):
    """
    Sprint 1: Core faculty profile model.
    Only essential identity fields are defined here.
    Academic relations (publications, education, etc.) are added in Sprint 2+.
    """
    __tablename__ = "faculty_profiles"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    # Personal Information
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    designation: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str | None] = mapped_column(String)
    
    # Text fields — will be passed to NLP pipeline (TF-IDF, keyword extraction) in Sprint 3
    bio: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[str | None] = mapped_column(Text)  # comma-separated; parsed by analytics service
    
    profile_image_url: Mapped[str | None] = mapped_column(String)

    # Timestamps for trend analytics (publication rate over time, activity tracking)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Sprint 1: One-to-one relationship back to the User model
    user = relationship("User", back_populates="profile")

    # Sprint 2+: Academic relationships will be added here in future sprints.
