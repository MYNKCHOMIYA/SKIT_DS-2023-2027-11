from sqlalchemy import String, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import date
import uuid


class Experience(Base):
    """
    Sprint 2 (Kunal - Backend): Professional experience record of a faculty member.
    Tracks jobs, positions and industry experience chronologically.
    """

    __tablename__ = "experience"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    faculty_id: Mapped[str] = mapped_column(
        ForeignKey("faculty_profiles.id", ondelete="CASCADE")
    )

    job_title: Mapped[str] = mapped_column(String, nullable=False)
    organization: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    employment_type: Mapped[str | None] = mapped_column(String)  # Full-time, Part-time

    # Relationships
    faculty = relationship("FacultyProfile", back_populates="experience")
