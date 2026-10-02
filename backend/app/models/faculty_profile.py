from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import uuid


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
    bio: Mapped[str | None] = mapped_column(Text)
    profile_image_url: Mapped[str | None] = mapped_column(String)

    # Sprint 1: One-to-one relationship back to the User model
    user = relationship("User", back_populates="profile")

    # Sprint 2+: Academic relationships will be added here in future sprints.
