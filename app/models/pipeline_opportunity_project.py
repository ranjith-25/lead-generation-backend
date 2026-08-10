import uuid
from sqlalchemy import String, DateTime, func, text,Enum , ForeignKey , Float , JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base
from app.schemas.pipeline_execution_status import PipelineExecutionStatus

class PipelineOpportunityProjectModel(Base):
    __tablename__ = "pipeline_opportunity_project"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    opportunity_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("opportunities.opportunityID",ondelete="CASCADE"))
    project_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("projects.project_id",ondelete="CASCADE"))
    project_name : Mapped[str] = mapped_column(String(255),nullable=False)
    match_score : Mapped[float] = mapped_column(Float,nullable=False)
    justification : Mapped[str] = mapped_column(String(500),nullable=False)
    matched_evidence : Mapped[list[str]] = mapped_column(JSON,nullable=False)
    
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