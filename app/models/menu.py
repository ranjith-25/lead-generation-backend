from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Menu(Base):
    __tablename__ = "menus"

    menu_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class MenuRole(Base):
    __tablename__ = "menu_roles"

    menu_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("menus.menu_id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.role_id", ondelete="CASCADE"),
        primary_key=True,
    )
    assignedAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
