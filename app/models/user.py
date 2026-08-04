import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.menu import Menu


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    roleName: Mapped[str] = mapped_column(String(50), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    menus: Mapped[list["Menu"]] = relationship(
        secondary="menu_roles", backref="roles", lazy="selectin"
    )

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fullName: Mapped[str] = mapped_column(String(100), nullable=False)
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
    reportingUser: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[reporting_to],
        remote_side=[user_id],
        backref="subordinates",
        lazy="selectin",
    )


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
