import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import RoleNotFoundException
from app.models.role import Role
from app.schemas.user import UserRoleChangeResult, UserRoleChangeUser
from app.services.db.role import get_role_by_id, get_role_by_name
from app.services.db.user import bulk_update_users_role, get_users_by_role_id


async def _resolve_role(db: AsyncSession, role: UUID | str) -> Role:
    try:
        role_id = UUID(str(role))
    except (ValueError, TypeError):
        role_id = None

    resolved = await get_role_by_id(db, role_id) if role_id else None

    if not resolved:
        resolved = await get_role_by_name(db, str(role))

    if not resolved:
        raise RoleNotFoundException(role)

    return resolved


async def change_users_role(
    db: AsyncSession,
    current_role: UUID | str,
    destination_role: UUID | str,
    dry_run: bool = False,
) -> UserRoleChangeResult:

    source = await _resolve_role(db, current_role)
    destination = await _resolve_role(db, destination_role)

    affected = await get_users_by_role_id(db, source.role_id)

    result = UserRoleChangeResult(
        current_role=source.roleName,
        current_role_id=source.role_id,
        destination_role=destination.roleName,
        destination_role_id=destination.role_id,
        changed_count=0,
        dry_run=dry_run,
        users=[UserRoleChangeUser.model_validate(user) for user in affected],
    )
    if source.role_id == destination.role_id:
        logging.info(f"Role change skipped: '{source.roleName}' is already the destination")
        return result

    if not affected:
        logging.info(f"Role change skipped: no users hold role '{source.roleName}'")
        return result

    if dry_run:
        logging.info(
            f"[dry run] would move {len(affected)} user(s) "
            f"from '{source.roleName}' to '{destination.roleName}'"
        )
        return result

    result.changed_count = await bulk_update_users_role(
        db, source.role_id, destination.role_id
    )

    logging.info(
        f"Moved {result.changed_count} user(s) "
        f"from '{source.roleName}' to '{destination.roleName}'"
    )

    return result
