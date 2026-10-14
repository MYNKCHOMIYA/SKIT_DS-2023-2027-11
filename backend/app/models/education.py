from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import date
import uuid


class Education(Base):
    """
    Sprint 2 (Kunal - Backend): Education background of a faculty member.
    Represents the academic qualifications of the faculty.
    """

    __tablename__ = "education"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    faculty_id: Mapped[str] = mapped_column(
        ForeignKey("faculty_profiles.id", ondelete="CASCADE")
    )

    degree: Mapped[str] = mapped_column(
        String, nullable=False
    )  # e.g., Ph.D., M.Tech, B.Tech
    institution: Mapped[str] = mapped_column(String, nullable=False)
    field_of_study: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)  # Null if currently pursuing
    grade: Mapped[str | None] = mapped_column(String)  # CGPA or Percentage

    # Relationships
    faculty = relationship("FacultyProfile", back_populates="education")
