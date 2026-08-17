from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.firebase_notification import FirebaseNotificationDTO


class GetFirebaseNotificationResponse(BaseResponse):
    firebaseNotification: Optional[FirebaseNotificationDTO] = Field(None, description="Firebase Notification")
    firebaseNotificationList: Optional[list[FirebaseNotificationDTO]] = Field(None, description="Firebase Notification List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreateFirebaseNotificationResponse(BaseResponse):
    newFirebaseNotification: FirebaseNotificationDTO = Field(..., description="New Firebase Notification Created")
    status_code: int = Field(200)


class UpdateFirebaseNotificationResponse(BaseResponse):
    updatedFirebaseNotification: FirebaseNotificationDTO = Field(..., description="Firebase Notification Updated")
    status_code: int = Field(200)


class DeleteFirebaseNotificationResponse(BaseResponse):
    status_code: int = Field(200)
