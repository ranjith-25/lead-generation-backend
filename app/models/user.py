import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user_personal_info import UserPersonalInfo


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashedPassword: Mapped[str | None] = mapped_column(String(150), nullable=True)
    refUID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    passwordResetAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    role_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("roles.role_id", ondelete="SET NULL"), nullable=True
    )
    reporting_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )
    specialization: Mapped[str] = mapped_column(String(100), nullable=True) 
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
