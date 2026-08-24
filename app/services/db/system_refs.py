"""Key -> id lookups for the rows the code addresses by a stable key.

Two ways to use a key, and the right one depends on the query:

* **Same table** - compare the key column directly, no round trip:
  `.where(Role.role_key.is_distinct_from(RoleKey.SUPER_ADMIN))`. Use `is_distinct_from`,
  never a bare `!=`: in SQL `NULL != 'super_admin'` evaluates to `NULL`, not `TRUE`, so a
  plain comparison silently drops every administrator-created row.

* **Different table** - resolve the key to an id here and compare ids:
  `.where(User.role_id.in_(await resolve_role_ids(db, [...])))`. Cheaper than joining and
  string-matching the display name, and it survives a rename.

Ids are cached per process. Only hits are cached, so a row seeded after boot is picked up
without a restart; keys are immutable and unsettable through the API, so a cached id can
only go stale if the row is deleted - hence `clear_system_ref_cache`, called from the role
and status delete services.
"""

import logging
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import OpportunityStatusKey, RoleKey, UserStatusKey
from app.models.opportunity_status import OpportunityStatus
from app.models.role import Role
from app.models.user_status import UserStatus

# (table, key) -> id
_ID_CACHE: dict[tuple[str, str], UUID] = {}


def clear_system_ref_cache() -> None:
    """Drop every cached id. Call after deleting a role or status row."""
    _ID_CACHE.clear()


async def _resolve(db: AsyncSession, table: str, id_col, key_col, key) -> UUID | None:
    cache_key = (table, key.value)
    if cache_key in _ID_CACHE:
        return _ID_CACHE[cache_key]

    try:
        result = await db.execute(select(id_col).where(key_col == key.value))
        row_id = result.scalars().first()
    except SQLAlchemyError:
        logging.exception("Could not resolve %s key: %s", table, key.value)
        raise

    if row_id is None:
        # Not cached - a row seeded later should be picked up without a restart.
        logging.warning("No %s row with key %r", table, key.value)
        return None

    _ID_CACHE[cache_key] = row_id
    return row_id


async def resolve_role_id(db: AsyncSession, key: RoleKey) -> UUID | None:
    return await _resolve(db, "roles", Role.role_id, Role.role_key, key)


async def resolve_role_ids(db: AsyncSession, keys: Sequence[RoleKey]) -> list[UUID]:
    """Ids for several role keys. Keys with no row contribute nothing, matching the
    behaviour of the role-name lookup this replaces."""
    ids = []
    for key in keys:
        role_id = await resolve_role_id(db, key)
        if role_id is not None:
            ids.append(role_id)
    return ids


async def resolve_user_status_id(db: AsyncSession, key: UserStatusKey) -> UUID | None:
    return await _resolve(db, "user_status", UserStatus.id, UserStatus.status_key, key)


async def resolve_opportunity_status_id(
    db: AsyncSession, key: OpportunityStatusKey
) -> UUID | None:
    return await _resolve(
        db, "opportunity_status", OpportunityStatus.id, OpportunityStatus.status_key, key
    )


async def warm_system_ref_cache(db: AsyncSession) -> list[str]:
    """Resolve every known key at startup and return the ones with no row.

    Reports rather than raises: a fresh database has to start so it can be seeded. The
    use sites raise `SystemRowMissingException` when they actually need a missing row.
    """
    missing: list[str] = []
    for table, resolver, keys in (
        ("roles", resolve_role_id, list(RoleKey)),
        ("user_status", resolve_user_status_id, list(UserStatusKey)),
        ("opportunity_status", resolve_opportunity_status_id, list(OpportunityStatusKey)),
    ):
        for key in keys:
            if await resolver(db, key) is None:
                missing.append(f"{table}.{key.value}")
    return missing
