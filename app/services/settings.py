import logging
from uuid import UUID

from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.exceptions.settings import (
    ConflictingPermissionToggleException,
    UnknownFeatureException,
    UnknownPermissionException,
)
from app.responses.settings import (
    GetRolePermissionMatrixResponse,
    UpdateRolePermissionMatrixResponse,
)
from app.schemas.settings import (
    FeaturePermissionRead,
    FeaturePermissionsRead,
    RolePermissionMatrixUpdate,
)
from app.services.db.role import get_role_by_id
from app.services.db.settings import (
    get_existing_feature_ids_db,
    get_existing_permission_ids_db,
    get_role_permission_matrix_db,
    set_role_permissions_db,
)


def _group_matrix_rows(rows: list[Row]) -> list[FeaturePermissionsRead]:
    """Collapse the flat feature x permission grid into one entry per feature.

    The query orders by feature display name then permission, and dicts keep insertion order,
    so both orderings survive the grouping without a second sort.
    """

    features: dict[UUID, FeaturePermissionsRead] = {}

    for row in rows:
        feature = features.get(row.feature_id)
        if feature is None:
            feature = FeaturePermissionsRead(
                featureID=row.feature_id,
                featureName=row.feature_name,
                featureKey=row.feature_key,
                permissions=[],
            )
            features[row.feature_id] = feature

        feature.permissions.append(
            FeaturePermissionRead(
                permissionID=row.permission_id,
                permissionKey=row.permission_key,
                permissionName=row.permission_name,
                assigned=row.assigned,
            )
        )

    return list(features.values())


def _collect_toggles(
    payload: RolePermissionMatrixUpdate,
) -> dict[tuple[UUID, UUID], bool]:

    toggles: dict[tuple[UUID, UUID], bool] = {}
    conflicts: list[tuple[UUID, UUID]] = []

    for feature in payload.features:
        for permission in feature.permissions:
            pair = (feature.featureID, permission.permissionID)
            previous = toggles.get(pair)

            if previous is not None and previous != permission.assigned:
                conflicts.append(pair)
                continue

            toggles[pair] = permission.assigned

    if conflicts:
        raise ConflictingPermissionToggleException(conflicts)

    return toggles


async def _validate_toggle_targets(
    db: AsyncSession, toggles: dict[tuple[UUID, UUID], bool]
) -> None:
    
    feature_ids = {feature_id for feature_id, _ in toggles}
    permission_ids = {permission_id for _, permission_id in toggles}

    unknown_features = feature_ids - await get_existing_feature_ids_db(db, feature_ids)
    if unknown_features:
        raise UnknownFeatureException(sorted(unknown_features, key=str))

    unknown_permissions = permission_ids - await get_existing_permission_ids_db(
        db, permission_ids
    )
    if unknown_permissions:
        raise UnknownPermissionException(sorted(unknown_permissions, key=str))


async def get_role_permission_matrix_service(
    db: AsyncSession, role_id: UUID
) -> GetRolePermissionMatrixResponse:
    try:
        role = await get_role_by_id(db, role_id)
        if role is None:
            raise NotFoundException()

        rows = await get_role_permission_matrix_db(db, role_id)

        return GetRolePermissionMatrixResponse(
            message="Role permissions fetched successfully",
            roleID=role.role_id,
            roleName=role.roleName,
            features=_group_matrix_rows(rows),
        )
    except NotFoundException:
        logging.exception("Could not find Role %s", role_id)
        raise
    except Exception:
        logging.exception("Some error occurred while building the role permission matrix")
        raise


async def update_role_permission_matrix_service(
    db: AsyncSession, role_id: UUID, payload: RolePermissionMatrixUpdate
) -> UpdateRolePermissionMatrixResponse:
    try:
        role = await get_role_by_id(db, role_id)
        if role is None:
            raise NotFoundException()

        toggles = _collect_toggles(payload)
        await _validate_toggle_targets(db, toggles)

        granted, revoked = await set_role_permissions_db(db, role_id, toggles)
        logging.info(
            "Role %s permissions updated: %s granted, %s revoked", role_id, granted, revoked
        )

        rows = await get_role_permission_matrix_db(db, role_id)

        return UpdateRolePermissionMatrixResponse(
            message="Role permissions updated successfully",
            roleID=role.role_id,
            roleName=role.roleName,
            features=_group_matrix_rows(rows),
        )
    except NotFoundException:
        logging.exception("Could not find Role %s", role_id)
        raise
    except Exception:
        logging.exception("Some error occurred while updating the role permission matrix")
        raise
