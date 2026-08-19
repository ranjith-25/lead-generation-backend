import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user_personal_info import UserPersonalInfo


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # Partial unique index instead of a plain UNIQUE on `email`: soft-deleted users keep
        # their row, and a plain constraint would burn that address forever — the same person
        # could never be re-invited, and a typo'd account would block its own correction.
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    hashedPassword: Mapped[str | None] = mapped_column(String(150), nullable=True)
    refUID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    passwordResetAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # RESTRICT rather than SET NULL: every user belongs to exactly one role, so a roleless row
    # is not a state the app can render or authorise - `require_permission` has nothing to walk.
    # SET NULL on a NOT NULL column is a promise the database cannot keep either; it would only
    # surface at delete time as a NOT NULL violation. RESTRICT states the actual rule - a role
    # that still holds users cannot be dropped - and `handle_delete_role` already honours it by
    # moving everyone onto the fallback `User` role before it deletes.
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False
    )
    reporting_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )

    # Users are never hard-deleted — ~25 tables carry a createdBy/updatedBy FK to this one,
    # most of them ON DELETE CASCADE, so a real DELETE would take the user's opportunities,
    # pipeline rows and seeded lookup data with it. See app/.docs/plans/user-soft-delete.md.
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    role: Mapped["Role"] = relationship(backref="users", lazy="selectin")
    personal_info: Mapped["UserPersonalInfo | None"] = relationship(
        "UserPersonalInfo",
        back_populates="user",
        lazy="selectin",
    )
    reportingUser: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[reporting_to],
        remote_side=[user_id],
        backref="subordinates",
        lazy="selectin",
    )

    @property
    def fullName(self) -> str:
        if self.personal_info:
            first = self.personal_info.first_name
            last = self.personal_info.last_name
            return f"{first} {last}".strip() if last else first
        return "Unknown User"

class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    expiresAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    isRevoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(backref="sessions", lazy="selectin")
