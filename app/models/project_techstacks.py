from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProjectTechStack(Base):
    __tablename__ = "project_techstacks"

    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        primary_key=True,
    )
    techstack_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tech_stacks.techstack_id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
