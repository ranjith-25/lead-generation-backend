from sqlalchemy.ext.asyncio import AsyncSession
import logging
from uuid import UUID

from app.services.db.permissions import (
    get_permissions,
    get_permission_by_id,
    create_permission,
    update_permission,
    delete_permission,
)
from app.responses.permissions import (
    GetPermissionResponse,
    CreatePermissionResponse,
    UpdatePermissionResponse,
    DeletePermissionResponse,
)
from app.schemas.permissions import (
    PermissionCreate,
    PermissionUpdate,
    PermissionDTO,
)
from app.models.permissions import Permission
from app.models.user import User
from app.exceptions.custom import NotFoundException


async def handle_get_permissions(db: AsyncSession, current_user: User) -> GetPermissionResponse:
    try:
        permissions = await get_permissions(db)

        if permissions is None:
            raise NotFoundException()

        permissions_response = GetPermissionResponse(
            permissionList=[PermissionDTO.model_validate(permission) for permission in permissions],
            message="Permissions fetched successfully",
            status_code=200
        )
        return permissions_response

    except NotFoundException as e:
        logging.exception("Could not find permissions")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while getting permissions list")
        raise e


async def handle_get_permission_by_id(db: AsyncSession, current_user: User, permission_id: UUID) -> GetPermissionResponse:
    try:
        permission_details = await get_permission_by_id(db, permission_id)

        if permission_details is None:
            raise NotFoundException()

        permission_response = GetPermissionResponse(
            permission=PermissionDTO.model_validate(permission_details),
            message="Permission fetched successfully",
            status_code=200
        )
        return permission_response

    except NotFoundException as e:
        logging.exception("Could not find permission")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while getting permission details")
        raise e


async def handle_create_permission(db: AsyncSession, current_user: User, permission_create: PermissionCreate) -> CreatePermissionResponse:
    try:
        new_permission = Permission(**permission_create.model_dump())
        permission = await create_permission(db, new_permission)
        permission_response = CreatePermissionResponse(
            newPermission=PermissionDTO.model_validate(permission),
            message="Permission created successfully",
            status_code=201
        )
        return permission_response

    except Exception as e:
        logging.exception("Some error occurred while creating permission")
        raise e


async def handle_update_permission(db: AsyncSession, current_user: User, permission_update: PermissionUpdate, permission_id: UUID) -> UpdatePermissionResponse:
    try:
        updated_data = permission_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_permission = await update_permission(db, updated_data, permission_id)

        if updated_permission is None:
            raise NotFoundException()

        permission_response = UpdatePermissionResponse(
            updatedPermission=PermissionDTO.model_validate(updated_permission),
            message="Permission updated successfully",
            status_code=200
        )
        return permission_response

    except NotFoundException as e:
        logging.exception("Could not find permission to update")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while updating permission")
        raise e


async def handle_delete_permission(db: AsyncSession, current_user: User, permission_id: UUID) -> DeletePermissionResponse:
    try:
        deleted_permission = await delete_permission(db, permission_id)

        if deleted_permission is None:
            raise NotFoundException()

        permission_response = DeletePermissionResponse(
            message="Permission deleted successfully",
            status_code=200
        )
        return permission_response

    except NotFoundException as e:
        logging.exception("Could not find permission to delete")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while deleting permission")
        raise e
