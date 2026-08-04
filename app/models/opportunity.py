import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.opportunity_status import OpportunityStatus
from app.models.user import User


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
    
    creator: Mapped[User] = relationship(
        "User", foreign_keys=[createdBy], lazy="selectin"
    )
    updater: Mapped[User] = relationship(
        "User", foreign_keys=[updatedBy], lazy="selectin"
    )

    @property
    def createdByName(self) -> str:
        return self.creator.fullName if self.creator else str(self.createdBy)

    @property
    def updatedByName(self) -> str:
        return self.updater.fullName if self.updater else str(self.updatedBy)
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
    job_posting_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("opportunity_status.id"), default=1, server_default="1", nullable=False)
    is_ai_scraped: Mapped[bool] = mapped_column(default=True, server_default="true", nullable=False)
    additional_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    status: Mapped[OpportunityStatus] = relationship(backref="opportunities", lazy="selectin")

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
