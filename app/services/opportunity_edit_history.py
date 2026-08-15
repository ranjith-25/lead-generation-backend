import math
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import PageName
from app.models.opportunity import Opportunity
from app.models.opportunity_edit_history import OpportunityEditHistory
from app.schemas.opportunity_edit_history import (
    OpportunityEditHistoryPaginatedResponse,
    OpportunityEditHistoryRead,
)
from app.services.db.opportunity import get_opportunity_by_id
from app.services.db.opportunity_edit_history import (
    get_opportunity_edit_history_db,
    stage_opportunity_edit_history,
)
from app.services.db.user import get_user_by_id

# Audit bookkeeping the history row already carries in its own columns — recording it inside
# `changes` too would put a meaningless entry on every single edit.
IGNORED_EDIT_FIELDS = {"updatedBy", "updatedAt", "createdBy", "createdAt", "opportunityID"}


def _json_safe(value):
    """Coerce an ORM value into something JSONB can store.

    UUID and datetime are the two that reach here routinely (status_id, assigned_to,
    posted dates) and neither survives json.dumps untouched.
    """
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


def build_opportunity_changes(opportunity: Opportunity, update_data: dict) -> dict:
    """Diff a pending update against the opportunity's current values.

    Must be called BEFORE the update is applied — the old values are read straight off the
    ORM object. Fields set to the value they already hold are left out, so a no-op edit
    records nothing.
    """
    changes: dict = {}

    for field, new_value in update_data.items():
        if field in IGNORED_EDIT_FIELDS:
            continue

        old_value = getattr(opportunity, field, None)
        if old_value == new_value:
            continue

        changes[field] = {"old": _json_safe(old_value), "new": _json_safe(new_value)}

    return changes


async def record_opportunity_edit(
    db: AsyncSession,
    opportunity: Opportunity,
    update_data: dict,
    user_id: UUID,
    page_name: PageName = PageName.OPPORTUNITY_ANALYSIS,
) -> None:
    """Stage an edit-history row for this update. No commit — the caller's commit covers it."""

    changes = build_opportunity_changes(opportunity, update_data)
    if not changes:
        return

    editor = await get_user_by_id(db, user_id)

    stage_opportunity_edit_history(
        db,
        OpportunityEditHistory(
            opportunity_id=opportunity.opportunityID,
            page_name=page_name,
            edited_by=user_id,
            edited_by_name=editor.fullName if editor else "Unknown User",
            changes=changes,
        ),
    )


async def get_opportunity_edit_history_service(
    db: AsyncSession,
    opportunityID: UUID | str,
    user_id: UUID,
    page_name: PageName | None = None,
    page: int = 1,
    size: int = 10,
) -> OpportunityEditHistoryPaginatedResponse:

    try:
        opp_id = UUID(str(opportunityID))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")

    history, total = await get_opportunity_edit_history_db(
        db, opp_id, page_name, page, size
    )

    return OpportunityEditHistoryPaginatedResponse(
        data=[OpportunityEditHistoryRead.model_validate(row) for row in history],
        total=total,
        page=page,
        size=size,
        total_pages=math.ceil(total / size) if total > 0 else 1,
    )
