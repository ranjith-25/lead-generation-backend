from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProjectDomain(Base):
    __tablename__ = "project_domains"

    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        primary_key=True,
    )
    domain_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("domains.domain_id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
