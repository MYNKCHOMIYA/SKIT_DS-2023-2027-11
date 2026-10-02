from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import uuid


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    code: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )  # e.g., "CSE", "ECE"

    # Relationships
    users = relationship("User", back_populates="department")
