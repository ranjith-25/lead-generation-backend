import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    opportunityID: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    createdBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    updatedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(100), nullable=True)
    posted_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    preferred_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    requirements: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    benefits: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    client_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    apply_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_job_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_proposal_questions: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    company_profile: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    additional_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
