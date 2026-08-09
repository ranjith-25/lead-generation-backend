import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_role import JobRole
    from app.models.user_status import UserStatus
    from app.models.branch import Branch


class UserPersonalInfo(Base):
    __tablename__ = "user_personal_info"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
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
    primary_role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True)
    highest_qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    year_of_passout: Mapped[int] = mapped_column(Integer, nullable=False)
    working_status_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_status.id", ondelete="RESTRICT"), nullable=False)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="personal_info", lazy="selectin")
    jobRole: Mapped["JobRole"] = relationship(lazy="selectin")
    userStatus: Mapped["UserStatus"] = relationship(lazy="selectin")
    branch: Mapped["Branch"] = relationship(lazy="selectin")
