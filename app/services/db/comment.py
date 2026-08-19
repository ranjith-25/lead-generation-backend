from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.config import PageName
from app.models.comment import Comment
from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel
from app.models.pipeline_opportunity_techincal_preperation import (
    PipelineOpportunityTechnicalPreperationModel,
)


async def add_comment_db(db: AsyncSession, comment: Comment) -> Comment:
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments_db(
    db: AsyncSession,
    page_name: PageName,
    entity_id: UUID,
    page: int,
    size: int,
) -> tuple[list[Comment], int]:
    """One page of TOP-LEVEL comments for one row, newest first, plus the total.

    Replies are excluded here on purpose - they are fetched in a single follow-up call to
    `get_replies_db` and grouped under their parents by the service, so the request costs two
    queries no matter how many comments there are.

    Soft-deleted rows are still returned: a removed comment renders as a placeholder so its
    surviving replies keep their place in the thread. Filtering them out here would make
    replies look orphaned.
    """

    # `Comment.replies` is lazy="selectin" on the model, which is right for any caller that
    # wants a whole thread object back. It is wrong here: the service assembles replies itself
    # from a single grouped `get_replies_db` call, so an eager load would redo that work per
    # page - and, the relationship being self-referential, keep recursing down the chain. The
    # explicit path wins, so every query in this module suppresses it. `author` stays eager:
    # the service reads it, and a lazy load outside the session raises MissingGreenlet.
    query = (
        select(Comment)
        .where(
            Comment.page_name == page_name,
            Comment.entity_id == entity_id,
            Comment.parent_comment_id.is_(None),
        )
        .options(noload(Comment.replies))
    )

    # Counted off the same filtered query, so the total always agrees with the page.
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total_count = total_result.scalar() or 0

    query = (
        query.order_by(Comment.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    result = await db.execute(query)

    return list(result.scalars().all()), total_count


async def get_replies_db(db: AsyncSession, parent_ids: list[UUID]) -> list[Comment]:
    """Every reply belonging to any of `parent_ids`, in one query, oldest first.

    Flat on purpose - the caller groups by `parent_comment_id` in Python. Looping a query per
    parent would turn one page of comments into N round trips.
    """

    # An empty IN () is a syntax error, and there is nothing to ask for anyway.
    if not parent_ids:
        return []

    query = (
        select(Comment)
        .where(Comment.parent_comment_id.in_(parent_ids))
        .order_by(Comment.created_at.asc())
        # A reply never has children - the service caps nesting at one level - so eager-loading
        # `replies` here is guaranteed-empty work.
        .options(noload(Comment.replies))
    )

    result = await db.execute(query)

    return list(result.scalars().all())


async def get_comment_by_id_db(db: AsyncSession, comment_id: UUID) -> Comment | None:
    # Callers are the parent lookup and the update/delete paths; none of them read `.replies`.
    query = select(Comment).where(Comment.id == comment_id).options(noload(Comment.replies))
    result = await db.execute(query)
    return result.scalars().first()


async def update_comment_db(
    db: AsyncSession, comment: Comment, update_data: dict
) -> Comment:
    """Persist `update_data` onto the row. `is_edited` is a business rule and is set by the
    service before it calls here, not inferred from the presence of an update."""

    for key, value in update_data.items():
        setattr(comment, key, value)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def soft_delete_comment_db(db: AsyncSession, comment: Comment) -> Comment:
    """Flag the row deleted and leave its replies alone - they stay readable under the
    placeholder the soft-deleted parent becomes."""

    comment.is_deleted = True
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_entity_opportunity_id_db(
    db: AsyncSession, page_name: PageName, entity_id: UUID
) -> UUID | None:
    """Map a (page, row) pair to the opportunity it hangs off, or `None` when the row does not
    exist. The single place that knows which table each `PageName` addresses; a fourth
    commentable page is one more branch here and no schema change.

    Returning `None` rather than raising keeps this layer free of HTTP concepts - the service
    turns the miss into `CommentEntityNotFoundException`.
    """

    if page_name == PageName.OPPORTUNITY_ANALYSIS:
        # The entity IS the opportunity on this page, so there is nothing to look up.
        return entity_id

    if page_name == PageName.RESOURCE_MATCH:
        query = select(PipelineOpportunityResourceModel.opportunity_id).where(
            PipelineOpportunityResourceModel.id == entity_id
        )
    elif page_name == PageName.TECHNICAL_PREPARATION:
        query = select(
            PipelineOpportunityTechnicalPreperationModel.opportunity_id
        ).where(PipelineOpportunityTechnicalPreperationModel.id == entity_id)
    else:
        return None

    result = await db.execute(query)
    return result.scalars().first()
