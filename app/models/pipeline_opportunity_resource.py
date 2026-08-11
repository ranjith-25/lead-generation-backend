import uuid
from sqlalchemy import String, DateTime, func, text,Enum , ForeignKey , Float , JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base
from app.schemas.pipeline_execution_status import PipelineExecutionStatus

class PipelineOpportunityResourceModel(Base):
    __tablename__ = "pipeline_opportunity_resource"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    opportunity_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("opportunities.opportunityID",ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    email : Mapped[str] = mapped_column(String(255),nullable=False)
    variant_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("profile_variants.profile_variant_id",ondelete="CASCADE"))
    variant_title : Mapped[str] = mapped_column(String(255),nullable=False)
    experience_years : Mapped[float] = mapped_column(Float,nullable=False)
    match_percentage : Mapped[float] = mapped_column(Float,nullable=False)
    matching_skills : Mapped[list[str]] = mapped_column(JSON,nullable=False)
    missing_skills : Mapped[list[str]] = mapped_column(JSON,nullable=False)
    justification : Mapped[str] = mapped_column(String(1000),nullable=False)
    
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    createdBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    updatedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )