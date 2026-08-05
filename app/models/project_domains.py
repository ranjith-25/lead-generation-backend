from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class ProjectDomain(Base):
    __tablename__ = "project_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=False)
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

    projects: Mapped[list["Projects"]] = relationship(
        back_populates="projectDomain"
    )