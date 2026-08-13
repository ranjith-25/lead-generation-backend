from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.notification import NotificationRead


class MarkNotificationReadResponse(BaseResponse):
    notification: NotificationRead = Field(..., description="The notification after being marked read")
    unread_count: int = Field(..., description="This user's remaining unread notifications, so the client can update its badge without a second request")


class MarkAllNotificationsReadResponse(BaseResponse):
    updated_count: int = Field(..., description="How many notifications were flipped from unread to read")
    unread_count: int = Field(..., description="This user's remaining unread notifications, so the client can update its badge without a second request")
