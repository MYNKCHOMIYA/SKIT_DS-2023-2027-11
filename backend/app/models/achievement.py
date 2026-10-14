from sqlalchemy import String, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import date
import uuid


class Achievement(Base):
    """
    Sprint 2 (Kunal - Backend): Awards, recognitions and memberships of faculty.
    Categories: Award, Recognition, Membership, Workshop
    """

    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    faculty_id: Mapped[str] = mapped_column(
        ForeignKey("faculty_profiles.id", ondelete="CASCADE")
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Award, Recognition, Membership, Workshop
    achievement_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)

    # Relationships
    faculty = relationship("FacultyProfile", back_populates="achievements")
