from pydantic import BaseModel, Field

from app.config import NotificationType


class FirebaseNotificationPayload(BaseModel):
    notification_type: NotificationType = NotificationType.EMPTY
    title: str
    body: str
    data: dict[str, str] | None = None


class SimplePushRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Push notification title")
    message: str = Field(..., min_length=1, description="Push notification body text")
    url: str | None = Field(None, max_length=500, description="Optional URL to open when notification is tapped")
    fcm_token: str = Field(..., min_length=1, max_length=512, description="FCM device token to send to")
