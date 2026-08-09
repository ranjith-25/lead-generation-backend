from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.responses.role_permissions import (
    RolePermissionCreate,
    RolePermissionRead,
    GetRolePermissionsResponse,
    GetRolePermissionResponse,
    CreateRolePermissionResponse,
    UpdateRolePermissionResponse,
)
from app.responses.base import BaseResponse
from app.models.role_permissions import RolePermission
from app.services.db.role_permissions import (
    get_role_permission_by_id_db,
    get_role_permission_by_details_db,
    get_all_role_permissions_db,
    add_role_permission_db,
    update_role_permission_db,
    delete_role_permission_db,
)
from app.services.db.user import get_user_by_id
from app.services.db.feature import get_feature_by_id_db

async def get_all_role_permissions_service(db: AsyncSession) -> GetRolePermissionsResponse:
    role_permissions = await get_all_role_permissions_db(db)
    role_permissions_read = [
        RolePermissionRead.model_validate(rp) for rp in role_permissions
    ]
    return GetRolePermissionsResponse(
        message="Role permissions fetched successfully",
        role_permissions=role_permissions_read
    )

async def get_role_permission_service(
    db: AsyncSession, rp_id: UUID | str
) -> GetRolePermissionResponse:
    try:
        parsed_id = UUID(str(rp_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Role Permission ID format")

    rp = await get_role_permission_by_id_db(db, parsed_id)
    if not rp:
        raise HTTPException(status_code=404, detail="Role permission mapping not found")

    return GetRolePermissionResponse(
        message="Role permission mapping fetched successfully",
        role_permission=RolePermissionRead.model_validate(rp)
    )

async def create_role_permission_service(
    db: AsyncSession, rp_data: RolePermissionCreate
) -> CreateRolePermissionResponse:

    # Check if a mapping already exists (even if soft-deleted)
    existing = await get_role_permission_by_details_db(
        db, rp_data.role_id, rp_data.feature_id, rp_data.permission_id
    )
    if existing:
        if not existing.isDeleted:
            raise HTTPException(
                status_code=400, detail="Role permission mapping already exists"
            )
        else:
            # Reactivate soft-deleted mapping
            updated = await update_role_permission_db(db, existing, {"isDeleted": False})
            return CreateRolePermissionResponse(
                message="Role permission mapping created successfully",
                role_permission=RolePermissionRead.model_validate(updated)
            )

    rp_dict = rp_data.model_dump()
    new_rp = RolePermission(**rp_dict)
    saved_rp = await add_role_permission_db(db, new_rp)
    return CreateRolePermissionResponse(
        message="Role permission mapping created successfully",
        role_permission=RolePermissionRead.model_validate(saved_rp)
    )

async def update_role_permission_service(
    db: AsyncSession, rp_id: UUID | str, rp_data: RolePermissionCreate
) -> UpdateRolePermissionResponse:
    try:
        parsed_id = UUID(str(rp_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Role Permission ID format")

    rp = await get_role_permission_by_id_db(db, parsed_id)
    if not rp:
        raise HTTPException(status_code=404, detail="Role permission mapping not found")

    # Check if the updated details would conflict with an existing active mapping (other than itself)
    conflict = await get_role_permission_by_details_db(
        db, rp_data.role_id, rp_data.feature_id, rp_data.permission_id
    )
    if conflict and conflict.role_permission_id != parsed_id:
        if not conflict.isDeleted:
            raise HTTPException(
                status_code=400,
                detail="Another active role permission mapping with these details already exists"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Another role permission mapping with these details exists (inactive)"
            )

    update_dict = rp_data.model_dump(exclude_unset=True)
    updated_rp = await update_role_permission_db(db, rp, update_dict)
    return UpdateRolePermissionResponse(
        message="Role permission mapping updated successfully",
        role_permission=RolePermissionRead.model_validate(updated_rp)
    )

async def delete_role_permission_service(
    db: AsyncSession, rp_id: UUID | str
) -> BaseResponse:
    try:
        parsed_id = UUID(str(rp_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Role Permission ID format")

    rp = await get_role_permission_by_id_db(db, parsed_id)
    if not rp:
        raise HTTPException(status_code=404, detail="Role permission mapping not found")

    await delete_role_permission_db(db, rp)
    return BaseResponse(message="Role permission mapping deleted successfully")
