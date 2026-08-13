import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.schemas.notification import NotificationType


class Notifications(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"),
        default=NotificationType.EMPTY,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    body: Mapped[str] = mapped_column(Text, nullable=False)

    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True, index=True
    )
