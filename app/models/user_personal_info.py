import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserPersonalInfo(Base):
    __tablename__ = "user_personal_info"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    work_email: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[str] = mapped_column(String(10), nullable=False)
    primary_role: Mapped[str] = mapped_column(String(100), nullable=False)
    branch: Mapped[str] = mapped_column(String(100), nullable=False)
    highest_qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    year_of_passout: Mapped[int] = mapped_column(Integer, nullable=False)
    working_status: Mapped[str] = mapped_column(String(50), nullable=False)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    user: Mapped["User"] = relationship(backref="personal_info", lazy="selectin")
