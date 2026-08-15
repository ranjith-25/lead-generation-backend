import math
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    EDIT_HISTORY_DATETIME_FORMAT,
    EDIT_HISTORY_ID_FIELDS,
    EDIT_HISTORY_OPAQUE_SENTENCE,
    EDIT_HISTORY_SENTENCES,
    EDIT_HISTORY_SUMMARY,
    EDIT_HISTORY_VALUE_MAX_LENGTH,
    OPPORTUNITY_FIELD_LABELS,
    PAGE_NAME_LABELS,
    EditChangeType,
    PageName,
)
from app.exceptions.opportunity import (
    InvalidOpportunityIdException,
    OpportunityNotFoundException,
)
from app.models.opportunity import Opportunity
from app.models.opportunity_edit_history import OpportunityEditHistory
from app.schemas.opportunity_edit_history import (
    OpportunityEditChangeRead,
    OpportunityEditHistoryPaginatedResponse,
    OpportunityEditHistoryRead,
)
from app.services.db.opportunity import get_all_opportunity_statuses_db, get_opportunity_by_id
from app.services.db.opportunity_edit_history import (
    get_opportunity_edit_history_db,
    stage_opportunity_edit_history,
)
from app.services.db.user import get_user_by_id, get_users_by_ids

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


# ---------------------------------------------------------------------------
# Read side: turning a stored diff into sentences
# ---------------------------------------------------------------------------


def _humanise(field: str) -> str:
    """Fallback label for a column nobody has named yet: `posted_date` -> `Posted Date`."""
    return field.replace("_", " ").strip().title()


def _is_empty(value) -> bool:
    """Whether a stored value counts as "no value" — drives ADDED vs UPDATED vs REMOVED."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return not value
    return False


def _truncate(text: str) -> str:
    if len(text) <= EDIT_HISTORY_VALUE_MAX_LENGTH:
        return text
    return text[:EDIT_HISTORY_VALUE_MAX_LENGTH].rstrip() + "…"


def _display_value(value, id_labels: dict[str, str], is_id_field: bool) -> str | None:
    """Format one stored value for a sentence, or None when it has no readable inline form.

    Returning None is what pushes the sentence to its opaque form, which is the point: a raw
    UUID or a serialised JSON blob in the middle of a sentence is worse than no value at all.
    """
    if _is_empty(value):
        return None

    if is_id_field:
        # Unresolved (row deleted since, or a value that was never an id) — stay opaque.
        return id_labels.get(str(value)) or None

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (list, tuple)):
        parts = [str(item).strip() for item in value if not _is_empty(item)]
        return _truncate(", ".join(parts)) if parts else None

    if isinstance(value, dict):
        return None

    return _truncate(str(value).strip())


def _change_type(old_value, new_value) -> EditChangeType:
    old_empty = _is_empty(old_value)
    new_empty = _is_empty(new_value)

    if old_empty and not new_empty:
        return EditChangeType.ADDED
    if new_empty and not old_empty:
        return EditChangeType.REMOVED
    return EditChangeType.UPDATED


def _format_at(value: datetime | None) -> str:
    """`edited_at` as it reads inside a sentence. Empty string keeps a null out of the text."""
    return value.strftime(EDIT_HISTORY_DATETIME_FORMAT) if value else ""


def _finish(sentence: str, at: str) -> str:
    """Drop the dangling connector when there is no timestamp to append.

    Every sentence template ends in " on {at}", so a missing timestamp would otherwise leave
    the sentence hanging on the preposition.
    """
    return sentence if at else sentence.removesuffix(" on ").rstrip()


def _sentence(
    editor: str,
    label: str,
    change_type: EditChangeType,
    old_display: str | None,
    new_display: str | None,
    at: str,
) -> str:
    required = {
        EditChangeType.ADDED: (new_display,),
        EditChangeType.REMOVED: (old_display,),
        EditChangeType.UPDATED: (old_display, new_display),
    }[change_type]

    if any(part is None for part in required):
        return _finish(
            EDIT_HISTORY_OPAQUE_SENTENCE.format(editor=editor, label=label, at=at), at
        )

    return _finish(
        EDIT_HISTORY_SENTENCES[change_type].format(
            editor=editor, label=label, old=old_display, new=new_display, at=at
        ),
        at,
    )


def _join_labels(labels: list[str]) -> str:
    if len(labels) == 1:
        return labels[0]
    return f"{', '.join(labels[:-1])} and {labels[-1]}"


def _build_change(
    editor: str, field: str, change, id_labels: dict[str, str], at: str
) -> OpportunityEditChangeRead:
    # Defensive: a hand-written or legacy row may hold a bare value instead of {old, new}.
    change = change if isinstance(change, dict) else {"old": None, "new": change}

    old_value = change.get("old")
    new_value = change.get("new")
    is_id_field = field in EDIT_HISTORY_ID_FIELDS

    label = OPPORTUNITY_FIELD_LABELS.get(field) or _humanise(field)
    old_display = _display_value(old_value, id_labels, is_id_field)
    new_display = _display_value(new_value, id_labels, is_id_field)
    change_type = _change_type(old_value, new_value)

    return OpportunityEditChangeRead(
        field=field,
        label=label,
        change_type=change_type,
        old=old_display,
        new=new_display,
        sentence=_sentence(editor, label, change_type, old_display, new_display, at),
    )


def build_edit_history_read(
    row: OpportunityEditHistory, id_labels: dict[str, dict[str, str]] | None = None
) -> OpportunityEditHistoryRead:
    """One stored history row -> the record the API returns, sentences included."""
    id_labels = id_labels or {}
    editor = row.edited_by_name or "Unknown User"
    changes = row.changes or {}
    page_label = PAGE_NAME_LABELS.get(row.page_name) or _humanise(
        str(getattr(row.page_name, "value", row.page_name))
    )

    at = _format_at(row.edited_at)

    details = [
        _build_change(editor, field, change, id_labels.get(field, {}), at)
        for field, change in changes.items()
    ]
    labels = [detail.label for detail in details]

    # A single-field edit already says everything in its own sentence — repeating it as a
    # summary would show the reader the same line twice.
    if len(details) == 1:
        sentence = details[0].sentence
    elif labels:
        sentence = _finish(
            EDIT_HISTORY_SUMMARY.format(
                editor=editor, fields=_join_labels(labels), page=page_label, at=at
            ),
            at,
        )
    else:
        sentence = _finish(
            EDIT_HISTORY_OPAQUE_SENTENCE.format(editor=editor, label=page_label, at=at), at
        )

    return OpportunityEditHistoryRead(
        id=row.id,
        opportunity_id=row.opportunity_id,
        page_name=row.page_name,
        edited_by=row.edited_by,
        edited_by_name=editor,
        edited_at=row.edited_at,
        sentence=sentence,
        changes=details,
    )


def _as_uuid(value) -> UUID | None:
    try:
        return UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


async def _resolve_id_labels(
    history: list[OpportunityEditHistory], db: AsyncSession
) -> dict[str, dict[str, str]]:
    """{field: {stored id: display name}} for the id-valued fields on this page of history.

    Resolved in one batch per field rather than per row, and only for the fields this page
    actually contains, so a history with no status or assignment edits costs no extra query.
    """
    pending: dict[str, set[str]] = {field: set() for field in EDIT_HISTORY_ID_FIELDS}

    for row in history:
        for field, change in (row.changes or {}).items():
            if field not in pending or not isinstance(change, dict):
                continue
            for value in (change.get("old"), change.get("new")):
                if not _is_empty(value):
                    pending[field].add(str(value))

    id_labels: dict[str, dict[str, str]] = {}

    if pending.get("status_id"):
        statuses = await get_all_opportunity_statuses_db(db)
        id_labels["status_id"] = {str(status.id): status.status for status in statuses}

    if pending.get("assigned_to"):
        user_ids = [uid for uid in map(_as_uuid, pending["assigned_to"]) if uid]
        users = await get_users_by_ids(db, user_ids)
        id_labels["assigned_to"] = {str(user.user_id): user.fullName for user in users}

    return id_labels


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
        raise InvalidOpportunityIdException(opportunityID)

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise OpportunityNotFoundException(opp_id)

    history, total = await get_opportunity_edit_history_db(
        db, opp_id, page_name, page, size
    )
    id_labels = await _resolve_id_labels(history, db)

    return OpportunityEditHistoryPaginatedResponse(
        data=[build_edit_history_read(row, id_labels) for row in history],
        total=total,
        page=page,
        size=size,
        total_pages=math.ceil(total / size) if total > 0 else 1,
    )
