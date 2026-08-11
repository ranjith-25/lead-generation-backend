import uuid

from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    func,
    text,
    Enum,
    ForeignKey,
    Float,
    JSON,
    Boolean,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.user import User


class PipelineOpportunityResourceModel(Base):
    __tablename__ = "pipeline_opportunity_resource"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "opportunities.opportunityID",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "profile_variants.profile_variant_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    variant_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    experience_years: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    match_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    matching_skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    missing_skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    justification: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    createdAt: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    createdBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    updatedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    approved_by_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approved_by],
        lazy="selectin",
    )

    user_details: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="selectin",
    )

    
    @property
    def reportingTo(self):
        try:
            if not self.user_details or not self.user_details.reportingUser:
                return None
            return self.user_details.reportingUser.fullName
        except Exception:
            return None

    @property
    def workingStatus(self):
        try:
            if not self.user_details or not self.user_details.personal_info or not self.user_details.personal_info.userStatus:
                return None
            user_status = self.user_details.personal_info.userStatus
            return getattr(user_status, "displayName", getattr(user_status, "status_name", None))
        except Exception:
            return None

    @property
    def primaryJobRole(self):
        try:
            if not self.user_details or not self.user_details.personal_info or not self.user_details.personal_info.primary_role_id or not self.user_details.personal_info.jobRole:
                return None
            return self.user_details.personal_info.jobRole.roleName
        except Exception:
            return None

    @property
    def resourceApprovedBy(self):
        try:
            if self.approved_by_user:
                return self.approved_by_user.fullName
            return None
        except Exception:
            return None

    __table_args__ = (
        Index(
            "uq_one_approved_resource_per_opportunity",
            "opportunity_id",
            unique=True,
            postgresql_where=text("is_approved = true"),
        ),
    )