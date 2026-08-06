from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func,ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.schemas.user_invitation import InvitationStatus


class UserInvitation(Base):
    __tablename__ = "user_invitations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    work_email : Mapped[str] = mapped_column(String(100), nullable=False, unique=False)

    roleID : Mapped[int] = mapped_column(Integer,
    ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False)


    reporting_to : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus),
        default=InvitationStatus.PENDING,
        nullable=False
    )

    user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True
    )

    is_deleted : Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    invitedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    updatedBy: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

