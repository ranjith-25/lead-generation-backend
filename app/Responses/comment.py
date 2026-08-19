from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.comment import CommentRead


class CommentResponse(BaseResponse):
    """Envelope for create, reply and update — every one of them returns the single comment it
    just wrote. Listing returns ``CommentPaginatedResponse`` directly, and the soft delete acks
    with a bare ``BaseResponse``."""

    data: CommentRead = Field(..., description="The comment after the write")
