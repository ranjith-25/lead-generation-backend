import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.custom import NotFoundException
from app.models.role import Role
from app.models.user import User
from app.responses.role import (
    CreateRoleResponse,
    DeleteRoleResponse,
    GetRoleResponse,
    UpdateRoleResponse,
)
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.services.db.role import (
    create_role,
    delete_role,
    get_all_roles,
    get_role_by_id,
    update_role,
)


async def handle_get_role(
    db: AsyncSession, current_user: User, role_id: UUID
) -> GetRoleResponse:
    try:
        role = await get_role_by_id(db, role_id)
        if role is None:
            raise NotFoundException()

        return GetRoleResponse(
            role=RoleRead.model_validate(role),
            message="Role fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Role")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Role")
        raise e


async def handle_get_all_roles(db: AsyncSession, current_user: User) -> list[RoleRead]:
    try:
        roles = await get_all_roles(db)
        return [RoleRead.model_validate(role) for role in roles]
    except Exception as e:
        logging.exception("Some error occurred while getting all Roles")
        raise e


async def handle_create_role(
    db: AsyncSession, current_user: User, role_create: RoleCreate
) -> CreateRoleResponse:
    try:
        new_role = Role(**role_create.model_dump())
        created_role = await create_role(db, new_role)
        return CreateRoleResponse(
            role=RoleRead.model_validate(created_role),
            message="Role created successfully",
            status_code=201,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Role")
        raise e


async def handle_update_role(
    db: AsyncSession, current_user: User, role_update: RoleUpdate, role_id: UUID
) -> UpdateRoleResponse:
    try:
        update_data = role_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_role = await update_role(db, update_data, role_id)
        if updated_role is None:
            raise NotFoundException()

        return UpdateRoleResponse(
            role=RoleRead.model_validate(updated_role),
            message="Role updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Role")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Role")
        raise e


async def handle_delete_role(
    db: AsyncSession, current_user: User, role_id: UUID
) -> DeleteRoleResponse:
    try:
        deleted_role = await delete_role(db, role_id)
        if deleted_role is None:
            raise NotFoundException()

        return DeleteRoleResponse(
            message="Role deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Role")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Role")
        raise e
