from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.config import NotificationType

class FirebaseTokenBase(BaseModel):
    fcm_token: str = Field(..., min_length=1, max_length=512)
    user_id: UUID = Field(..., description="User ID")
    is_active: bool = Field(True)


class FirebaseTokenDTO(FirebaseTokenBase):
    id: UUID = Field(..., description="Firebase Token ID")
    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)
    created_by: Optional[UUID] = Field(None)
    updated_by: Optional[UUID] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class FirebaseTokenCreate(BaseModel):
    fcm_token: str = Field(..., min_length=1, max_length=512)


class FirebaseTokenUpdate(FirebaseTokenBase):
    fcm_token: Optional[str] = Field(None, min_length=1, max_length=512)
    user_id: Optional[UUID] = Field(None)
    is_active: Optional[bool] = Field(None)


class FirebaseNotificationPayload(BaseModel):
    notification_type: NotificationType = NotificationType.EMPTY
    title: str
    body: str
    data: dict[str, str] | None = None