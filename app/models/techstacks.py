from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class TechStacks(Base):
    __tablename__ = 'tech_stacks'

    techstack_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    techstack_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255)
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    createdBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    updatedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    projects: Mapped[List["Projects"]] = relationship(
        secondary="project_techstacks",
        back_populates="techstacks"
    )
