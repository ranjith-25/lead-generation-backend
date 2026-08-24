from datetime import datetime
from typing import TYPE_CHECKING

import uuid
from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.menu import Menu
    from app.models.role_permissions import RolePermission


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    roleName: Mapped[str] = mapped_column(String(50), nullable=False)

    # Stable identity for the rows the code addresses. Null for administrator-created
    # rows, which no code refers to. See app/config/system_keys.py.
    role_key: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )
    
    is_legacy_role: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    menus: Mapped[list["Menu"]] = relationship(
        secondary="menu_roles", backref="roles", lazy="selectin"
    )

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin"
    )