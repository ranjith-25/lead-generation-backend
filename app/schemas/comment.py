from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.config import PageName


class CommentCreate(BaseModel):
    """A new comment, or a reply when ``parent_comment_id`` is set.

    There is no separate reply endpoint — the same POST covers both. Nesting is capped at one
    level by the service: a parent that itself has a parent is re-pointed to the grandparent.
    """

    comment: str = Field(..., min_length=1, max_length=2000, description="The comment body")
    parent_comment_id: UUID | None = Field(
        None, description="Set to reply to an existing comment; omit for a top-level comment"
    )


class CommentUpdate(BaseModel):
    """Edit of an existing comment. Author-only, and it flips ``is_edited`` on the row."""

    comment: str = Field(..., min_length=1, max_length=2000, description="The replacement comment body")


class CommentRead(BaseModel):
    """One comment, with its replies inlined.

    ``created_by_name`` is the snapshot taken at write time, so a thread still reads correctly
    after its author is soft-deleted and ``created_by`` goes null. A soft-deleted comment is
    still returned (``is_deleted = True``) so the thread keeps its shape.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    page_name: PageName
    entity_id: UUID
    opportunity_id: UUID
    parent_comment_id: UUID | None = None
    comment: str
    created_by: UUID | None = None
    created_by_name: str
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None
    reply_count: int = Field(0, description="Number of replies attached to this comment")
    replies: list["CommentRead"] = Field(
        default_factory=list,
        description="Direct replies, oldest first; always empty on a reply itself (one level of nesting)",
    )


CommentRead.model_rebuild()


class CommentPaginatedResponse(BaseModel):
    """Pagination counts **top-level** comments only — replies ride inside their parent's
    ``replies`` list and are never paginated separately."""

    data: list[CommentRead]
    total: int
    page: int
    size: int
    total_pages: int
