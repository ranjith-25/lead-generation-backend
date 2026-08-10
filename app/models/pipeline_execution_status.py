import uuid
from sqlalchemy import String, DateTime, func, text,Enum , ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base
from app.schemas.pipeline_execution_status import PipelineExecutionStatus

class PipelineExecutionStatusModel(Base):
    __tablename__ = "pipeline_execution_status"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    projects : Mapped[Enum] = mapped_column(
        Enum(PipelineExecutionStatus),default=PipelineExecutionStatus.PENDING,nullable=False
    )
    salesEnablement : Mapped[Enum] = mapped_column(
        Enum(PipelineExecutionStatus),default=PipelineExecutionStatus.PENDING,nullable=False
    )
    resourceMatch : Mapped[Enum] = mapped_column(
        Enum(PipelineExecutionStatus),default=PipelineExecutionStatus.PENDING,nullable=False
    )
    technicalPreperation : Mapped[Enum] = mapped_column(
        Enum(PipelineExecutionStatus),default=PipelineExecutionStatus.PENDING,nullable=False
    )

    execution_message : Mapped[str] = mapped_column(String(255),nullable=True)

    opportunity_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("opportunities.opportunityID",ondelete="CASCADE"))
    
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