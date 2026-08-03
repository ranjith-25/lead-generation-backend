import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class SalesEnablement(Base):
    __tablename__ = "sales_enablement"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunityID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.opportunityID", ondelete="CASCADE"), nullable=False, unique=True
    )
    suggested_questions: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    sales_talking_points: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    outreach_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevant_projects: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    
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
