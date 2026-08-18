from pydantic import BaseModel, Field

from app.responses.base import BaseResponse


class FirebasePushSendResult(BaseModel):
    """Result of sending push notifications to one user's tokens."""
    success_count: int = Field(0)
    failure_count: int = Field(0)
    tokens_cleaned: int = Field(0, description="Invalid tokens deactivated after send")


class FirebasePushBatchResult(BaseModel):
    """Aggregate result of sending pushes to multiple users."""
    total_users: int
    total_success: int
    total_failures: int
    total_tokens_cleaned: int


class SimplePushResponse(BaseResponse):
    """Response for the simple push notification endpoint."""
    success: bool
    message_id: str | None = None


class FirebasePushResponse(BaseResponse):
    """Response wrapping a batch push result."""
    result: FirebasePushBatchResult
