from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.config import NotificationType


class NotificationContentBase(BaseModel):
    """Shared knobs for building a notification out of the configured templates."""

    notification_type: NotificationType = NotificationType.EMPTY
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Values substituted into the configured title/body/url templates, e.g. {'opportunity_id': '...'}",
    )
    title: str | None = Field(None, max_length=255, description="Overrides the configured title")
    body: str | None = Field(None, description="Overrides the configured body")
    url: str | None = Field(None, max_length=500, description="Overrides the configured navigation url")
    created_by: UUID | None = None


class NotificationCreateSchema(NotificationContentBase):
    user_id: UUID


class NotificationBulkCreateSchema(NotificationContentBase):
    user_ids: list[UUID] = Field(default_factory=list)


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notification_type: NotificationType
    title: str
    body: str
    url: str | None = None
    is_read: bool
    read_at: datetime | None = None
    user_id: UUID
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None


class NotificationUpdate(BaseModel):
    is_read: bool | None = None
    read_at: datetime | None = None


class NotificationFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    is_read: bool | None = None
    notification_type: list[NotificationType] | None = None


class NotificationPaginatedResponse(BaseModel):
    items: list[NotificationRead]
    total: int
    unread_count: int
    page: int
    limit: int
    total_pages: int