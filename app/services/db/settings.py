import logging
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature import Feature
from app.models.permissions import Permission
from app.models.role_permissions import RolePermission


async def get_role_permission_matrix_db(db: AsyncSession, role_id: UUID) -> list[Row]:
    stmt = (
        select(
            Feature.feature_id,
            Feature.display_name.label("feature_name"),
            Feature.feature_key,
            Feature.parent_feature_id,
            Permission.permission_id,
            Permission.permission_key,
            Permission.display_name.label("permission_name"),
            RolePermission.role_permission_id.is_not(None).label("assigned"),
        )
        .select_from(Feature)
        # cross join, deliberately unfiltered: every permission row is a column on the grid.
        # Narrowing it to create/read/update/delete hid the permissions that are enforced but
        # are not CRUD (approve, select_resource, ...), leaving them ungrantable from the screen
        .join(Permission, sa.true())
        .outerjoin(
            RolePermission,
            sa.and_(
                RolePermission.feature_id == Feature.feature_id,
                RolePermission.permission_id == Permission.permission_id,
                RolePermission.role_id == role_id,
                # revoking a permission soft-deletes the row instead of removing it, so a
                # revoked permission would still read as assigned without this
                RolePermission.isDeleted.is_(False),
            ),
        )
        .order_by(
            Feature.display_name,
            Feature.feature_id,
            # alphabetical; permission_id only breaks ties, so the column order stays stable
            # if two permissions ever share a display name
            Permission.display_name,
            Permission.permission_id,
        )
    )

    try:
        result = await db.execute(stmt)
        return list(result.all())
    except SQLAlchemyError:
        logging.exception("Could not fetch the permission matrix for role_id: %s", role_id)
        raise


async def get_existing_feature_ids_db(
    db: AsyncSession, feature_ids: set[UUID]
) -> set[UUID]:
    """Which of `feature_ids` actually exist — used to reject a bad payload up front."""

    try:
        result = await db.execute(
            select(Feature.feature_id).where(Feature.feature_id.in_(feature_ids))
        )
        return set(result.scalars().all())
    except SQLAlchemyError:
        logging.exception("Could not verify the features in the permission payload")
        raise


async def get_existing_permission_ids_db(
    db: AsyncSession, permission_ids: set[UUID]
) -> set[UUID]:
    try:
        result = await db.execute(
            select(Permission.permission_id).where(
                Permission.permission_id.in_(permission_ids)
            )
        )
        return set(result.scalars().all())
    except SQLAlchemyError:
        logging.exception("Could not verify the permissions in the permission payload")
        raise


async def set_role_permissions_db(
    db: AsyncSession,
    role_id: UUID,
    desired: dict[tuple[UUID, UUID], bool],
) -> tuple[int, int]:

    try:
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                sa.tuple_(RolePermission.feature_id, RolePermission.permission_id).in_(
                    list(desired.keys())
                ),
            )
        )

        # the table has no unique constraint on (role, feature, permission), so a pair can own
        # more than one row; they all have to move together or the pair stays half-granted
        existing: dict[tuple[UUID, UUID], list[RolePermission]] = {}
        for row in result.scalars().all():
            existing.setdefault((row.feature_id, row.permission_id), []).append(row)

        granted = 0
        revoked = 0

        for (feature_id, permission_id), assigned in desired.items():
            rows = existing.get((feature_id, permission_id))

            if not rows:
                # revoking a pair that was never granted is already the desired state
                if assigned:
                    db.add(
                        RolePermission(
                            role_id=role_id,
                            feature_id=feature_id,
                            permission_id=permission_id,
                            isDeleted=False,
                        )
                    )
                    granted += 1
                continue

            # isDeleted == assigned is exactly the "row disagrees with the toggle" case:
            # deleted row + switch on, or live row + switch off
            changed = False
            for row in rows:
                if row.isDeleted == assigned:
                    row.isDeleted = not assigned
                    changed = True

            if changed:
                if assigned:
                    granted += 1
                else:
                    revoked += 1

        await db.commit()
        return granted, revoked
    except SQLAlchemyError:
        await db.rollback()
        logging.exception("Could not update the permissions for role_id: %s", role_id)
        raise
