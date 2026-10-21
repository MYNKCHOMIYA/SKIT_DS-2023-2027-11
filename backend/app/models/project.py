from sqlalchemy import String, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import date
import uuid


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    faculty_id: Mapped[str] = mapped_column(
        ForeignKey("faculty_profiles.id", ondelete="CASCADE")
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    funding_agency: Mapped[str | None] = mapped_column(String)
    budget: Mapped[float | None] = mapped_column(Numeric(10, 2))  # Allows for decimals
    status: Mapped[str] = mapped_column(
        String, default="Ongoing"
    )  # Ongoing, Completed, Proposed
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)

    team_members: Mapped[str | None] = mapped_column(String)
    project_documents_url: Mapped[str | None] = mapped_column(String)

    # Relationships
    faculty = relationship("FacultyProfile", back_populates="projects")
