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
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.user import User
from app.schemas.pipeline_opportunity_resource import ApprovalStatus


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

    candidate_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
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

    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.SUGGESTED,
        nullable=False,
    )

    is_auto_approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )

    # Stores the user who is responsible/authorized to approve
    # this resource. This can be either a TL or a Manager.
    #
    # The frontend determines the approval authority based on
    # the selected users and sends this user ID to the backend.
    approval_authority_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # Stores the user who actually approved the resource.
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    reject_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    assigned_to_tl_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    rejected_by: Mapped[uuid.UUID | None] = mapped_column(
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

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    approval_authority_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approval_authority_id],
        lazy="selectin",
    )

    approved_by_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approved_by],
        lazy="selectin",
    )

    rejected_by_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[rejected_by],
        lazy="selectin",
    )

    assigned_to_tl_by_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_to_tl_by],
        lazy="selectin",
    )

    user_details: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="selectin",
    )

    # ---------------------------------------------------------
    # Computed Properties
    # ---------------------------------------------------------

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
            if (
                not self.user_details
                or not self.user_details.personal_info
                or not self.user_details.personal_info.userStatus
            ):
                return None

            user_status = self.user_details.personal_info.userStatus

            return getattr(
                user_status,
                "displayName",
                getattr(user_status, "status_name", None),
            )

        except Exception:
            return None

    @property
    def primaryJobRole(self):
        try:
            if (
                not self.user_details
                or not self.user_details.personal_info
                or not self.user_details.personal_info.primary_role_id
                or not self.user_details.personal_info.jobRole
            ):
                return None

            return self.user_details.personal_info.jobRole.roleName

        except Exception:
            return None

    @property
    def approvalAuthority(self):
        try:
            if self.approval_authority_user:
                return self.approval_authority_user.fullName

            return None

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

    @property
    def resourceRejectedBy(self):
        try:
            if self.rejected_by_user:
                return self.rejected_by_user.fullName

            return None

        except Exception:
            return None

    @property
    def resourceAssignedToTLBy(self):
        try:
            if self.assigned_to_tl_by_user:
                return self.assigned_to_tl_by_user.fullName

            return None

        except Exception:
            return None