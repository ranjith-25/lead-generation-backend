import math
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import PAGE_NAME_LABELS, LogAction, PageName
from app.exceptions.comment import (
    CommentEditNotAllowedException,
    CommentEntityNotFoundException,
    CommentNotFoundException,
)
from app.exceptions.opportunity import OpportunityNotFoundException
from app.models.comment import Comment
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.comment import CommentResponse
from app.schemas.comment import (
    CommentCreate,
    CommentPaginatedResponse,
    CommentRead,
    CommentUpdate,
)
from app.services.db.comment import (
    add_comment_db,
    get_comment_by_id_db,
    get_comments_db,
    get_entity_opportunity_id_db,
    get_replies_db,
    soft_delete_comment_db,
    update_comment_db,
)
from app.services.db.opportunity import get_opportunity_by_id
from app.services.system_log import log_activity

UNKNOWN_USER = "Unknown User"


# ---------------------------------------------------------------------------
# Addressing and access
# ---------------------------------------------------------------------------


async def resolve_entity(db: AsyncSession, page_name: PageName, entity_id: UUID) -> UUID:
    """The single place that maps a page + row to the opportunity it hangs off.

    `comments.entity_id` carries no foreign key — it points at one of three tables depending
    on `page_name` — so this lookup is what a constraint would otherwise be, and the
    `opportunity_id` it returns is the real cascading FK stored on the row.

    A fourth commentable page costs one branch in `get_entity_opportunity_id_db` and nothing
    anywhere else.
    """

    opportunity_id = await get_entity_opportunity_id_db(db, page_name, entity_id)
    if not opportunity_id:
        raise CommentEntityNotFoundException()

    return opportunity_id


async def check_comment_access(
    db: AsyncSession, page_name: PageName, entity_id: UUID, user_id: UUID
) -> UUID:
    """Resolve the entity, then re-check it through the opportunity ownership scope.

    Both halves are required on every entry point. `resolve_entity` only proves the row
    exists; `get_opportunity_by_id` is what applies the `createdBy` scope, so skipping it
    would let any authenticated user read and write comments on someone else's opportunity
    through all three pages.
    """

    opportunity_id = await resolve_entity(db, page_name, entity_id)

    opportunity = await get_opportunity_by_id(db, opportunity_id, user_id)
    if not opportunity:
        raise OpportunityNotFoundException(opportunity_id)

    return opportunity_id


def _page_label(page_name: PageName) -> str:
    return PAGE_NAME_LABELS.get(page_name) or str(getattr(page_name, "value", page_name))


def _log_details(page_name: PageName, entity_id: UUID, opportunity_id: UUID, **extra) -> dict:
    """Log payload shared by all four actions.

    The page lives here rather than in the action name, so a fourth commentable page adds no
    `LogAction` members (plan task 3.1.3).
    """

    details = {
        "page": _page_label(page_name),
        "entity_id": entity_id,
        "opportunity_id": opportunity_id,
    }
    details.update(extra)
    return details


# ---------------------------------------------------------------------------
# ORM -> DTO
# ---------------------------------------------------------------------------


def _build_comment_read(row: Comment, replies: list[Comment] | None = None) -> CommentRead:
    """Field-by-field on purpose: `model_validate` would walk `Comment.replies`, and that
    relationship is loaded per-parent by the ORM rather than by the single fan-out query the
    list service already ran. Building the DTO by hand keeps the read at two queries and
    keeps a soft-deleted parent's surviving replies attached where the service put them.
    """

    reply_reads = [_build_comment_read(reply) for reply in (replies or [])]

    return CommentRead(
        id=row.id,
        page_name=row.page_name,
        entity_id=row.entity_id,
        opportunity_id=row.opportunity_id,
        parent_comment_id=row.parent_comment_id,
        comment=row.comment,
        created_by=row.created_by,
        created_by_name=row.created_by_name or UNKNOWN_USER,
        is_edited=row.is_edited,
        is_deleted=row.is_deleted,
        created_at=row.created_at,
        updated_at=row.updated_at,
        reply_count=len(reply_reads),
        replies=reply_reads,
    )


# ---------------------------------------------------------------------------
# Write side
# ---------------------------------------------------------------------------


async def _resolve_parent(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    parent_comment_id: UUID | None,
) -> UUID | None:
    """The id a new reply should actually hang off, or None for a top-level comment (C-D5).

    Two rules:

    1. A parent that belongs to a different `(page_name, entity_id)` is not addressable from
       this route at all, so it reads as a missing comment rather than a forbidden one —
       reporting it as "wrong page" would confirm that someone else's comment exists.
    2. Nesting caps at one level: replying to a reply re-points at that reply's parent. One
       hop is enough because the cap is enforced on every write, so a stored
       `parent_comment_id` always names a top-level comment.
    """

    if not parent_comment_id:
        return None

    parent = await get_comment_by_id_db(db, parent_comment_id)
    if not parent:
        raise CommentNotFoundException()

    if parent.page_name != page_name or parent.entity_id != entity_id:
        raise CommentNotFoundException()

    return parent.parent_comment_id or parent.id


async def create_comment_service(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    comment_data: CommentCreate,
    current_user: User,
) -> CommentResponse:
    """Create a comment, or a reply when `parent_comment_id` is set — one route covers both."""

    opportunity_id = await check_comment_access(db, page_name, entity_id, current_user.user_id)

    parent_comment_id = await _resolve_parent(
        db, page_name, entity_id, comment_data.parent_comment_id
    )

    new_comment = Comment(
        page_name=page_name,
        entity_id=entity_id,
        opportunity_id=opportunity_id,
        parent_comment_id=parent_comment_id,
        comment=comment_data.comment,
        created_by=current_user.user_id,
        # Snapshot, not a join: the FK goes null when the author is soft-deleted and
        # User.fullName follows later renames, but a thread must show who said it at the time.
        created_by_name=current_user.fullName or UNKNOWN_USER,
    )

    await log_activity(
        db,
        LogAction.COMMENT_REPLIED if parent_comment_id else LogAction.COMMENT_ADDED,
        current_user,
        entity_type="comment",
        entity_name=_page_label(page_name),
        details=_log_details(
            page_name,
            entity_id,
            opportunity_id,
            parent_comment_id=parent_comment_id,
        ),
    )

    saved_comment = await add_comment_db(db, new_comment)

    return CommentResponse(
        message="Comment added successfully",
        data=_build_comment_read(saved_comment),
    )


async def update_comment_service(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    comment_id: UUID,
    comment_data: CommentUpdate,
    current_user: User,
) -> CommentResponse:
    """Edit a comment. Author-only regardless of role (C-D3)."""

    opportunity_id = await check_comment_access(db, page_name, entity_id, current_user.user_id)

    comment = await _get_editable_comment(db, page_name, entity_id, comment_id, current_user)

    update_data = {
        "comment": comment_data.comment,
        # Flipped here rather than in the DB layer: the flag describes the edit, and the DB
        # layer only applies whatever dict it is handed.
        "is_edited": True,
    }

    await log_activity(
        db,
        LogAction.COMMENT_UPDATED,
        current_user,
        entity_type="comment",
        entity_id=comment.id,
        entity_name=_page_label(page_name),
        details=_log_details(page_name, entity_id, opportunity_id, comment_id=comment.id),
    )

    updated_comment = await update_comment_db(db, comment, update_data)

    return CommentResponse(
        message="Comment updated successfully",
        data=_build_comment_read(updated_comment),
    )


async def delete_comment_service(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    comment_id: UUID,
    current_user: User,
) -> BaseResponse:
    """Soft delete, author-only on the same rule as editing (C-D4).

    Replies are left alone: the parent row stays in the list as a removed-comment placeholder
    so the thread keeps its shape and the answers to it stay readable.
    """

    opportunity_id = await check_comment_access(db, page_name, entity_id, current_user.user_id)

    comment = await _get_editable_comment(db, page_name, entity_id, comment_id, current_user)

    await log_activity(
        db,
        LogAction.COMMENT_DELETED,
        current_user,
        entity_type="comment",
        entity_id=comment.id,
        entity_name=_page_label(page_name),
        details=_log_details(page_name, entity_id, opportunity_id, comment_id=comment.id),
    )

    await soft_delete_comment_db(db, comment)

    return BaseResponse(message="Comment deleted successfully")


async def _get_editable_comment(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    comment_id: UUID,
    current_user: User,
) -> Comment:
    """The row an edit or a delete is allowed to touch, or the exception explaining why not.

    A comment addressed through the wrong page or the wrong entity is a 404, not a 403 — the
    caller proved access to *this* entity, not to whichever one the id really belongs to. A
    soft-deleted row is also a 404, so a stale id a client still holds cannot resurrect it.
    """

    comment = await get_comment_by_id_db(db, comment_id)
    if not comment:
        raise CommentNotFoundException()

    if comment.page_name != page_name or comment.entity_id != entity_id:
        raise CommentNotFoundException()

    if comment.is_deleted:
        raise CommentNotFoundException()

    if comment.created_by != current_user.user_id:
        raise CommentEditNotAllowedException()

    return comment


# ---------------------------------------------------------------------------
# Read side
# ---------------------------------------------------------------------------


async def get_comments_service(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    current_user: User,
    page: int = 1,
    size: int = 10,
) -> CommentPaginatedResponse:
    """One page of top-level comments with their replies inlined.

    Two queries whatever the comment count: the page of parents, then every reply for that
    page in a single fan-out, grouped here in Python. Pagination counts top-level comments
    only — replies ride inside their parent and are never paginated separately.
    """

    await check_comment_access(db, page_name, entity_id, current_user.user_id)

    comments, total = await get_comments_db(db, page_name, entity_id, page, size)

    replies_by_parent: dict[UUID, list[Comment]] = {}
    parent_ids = [comment.id for comment in comments]

    if parent_ids:
        for reply in await get_replies_db(db, parent_ids):
            replies_by_parent.setdefault(reply.parent_comment_id, []).append(reply)

    return CommentPaginatedResponse(
        data=[
            _build_comment_read(comment, replies_by_parent.get(comment.id))
            for comment in comments
        ],
        total=total,
        page=page,
        size=size,
        total_pages=math.ceil(total / size) if total > 0 else 1,
    )
