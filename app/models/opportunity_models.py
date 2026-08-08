from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Opportunity_Projects(Base):
    __tablename__ = "opportunity_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    opportunity_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    project_id : int = mapped_column(Integer, nullable=False)
    project_name : str = mapped_column(String(255), nullable=False)
    match_score : float = mapped_column(Float, nullable=False)
    justification : str = mapped_column(String(255), nullable=False)
    matched_evidence : list[str] = mapped_column(JSONB, nullable=False)

    createdBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    updatedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
