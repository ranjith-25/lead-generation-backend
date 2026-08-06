import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_role import JobRole
    from app.models.user_status import UserStatus


class UserPersonalInfo(Base):
    __tablename__ = "user_personal_info"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(String(10), nullable=False)
    primary_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)
    branch: Mapped[str] = mapped_column(String(100), nullable=False)
    highest_qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    year_of_passout: Mapped[int] = mapped_column(Integer, nullable=False)
    working_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_status.id", ondelete="RESTRICT"), nullable=False)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="personal_info", lazy="selectin")
    jobRole: Mapped["JobRole"] = relationship(lazy="selectin")
    userStatus: Mapped["UserStatus"] = relationship(lazy="selectin")
