from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.schemas.notification import NotificationType
class Notification(Base):
    __tablename__ = "notifications"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True
    )

    notification_type = mapped_column(
        Enum(NotificationType),
        default=NotificationType.INFO,
        nullable=False
    )

    title = mapped_column(
        String(255),
        nullable=False
    )

    body = mapped_column(
        Text,
        nullable=False
    )

    url = mapped_column(
        String(500),
        nullable=True
    )

    is_read = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    read_at = mapped_column(
        DateTime,
        nullable=True
    )

    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    created_by = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )

    updated_by = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )

    created_at = mapped_column(
        DateTime,
        index=True
    )

    updated_at = mapped_column(
        DateTime,
        index=True
    )