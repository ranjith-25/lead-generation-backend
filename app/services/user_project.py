import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.exceptions.custom import NotFoundException
from app.models.user_project import UserProject
from app.models.user import User
from app.responses.user_project import (
    CreateUserProjectResponse,
    DeleteUserProjectResponse,
    GetUserProjectResponse,
    UpdateUserProjectResponse,
)
from app.schemas.user_project import UserProjectCreate, UserProjectDTO, UserProjectUpdate
from app.services.db.user_project import (
    create_user_project,
    delete_user_project,
    get_all_user_projects,
    get_user_project_by_id,
    update_user_project,
)


async def handle_search_user_projects(
    db: AsyncSession, current_user: User, user_id: UUID | None = None
) -> GetUserProjectResponse:
    try:
        user_projects = await get_all_user_projects(db, user_id)

        return GetUserProjectResponse(
            userProjectList=[UserProjectDTO.model_validate(up) for up in user_projects],
            message="User Projects fetched successfully")
    except Exception as e:
        logging.exception("Some error occurred while getting User Projects list")
        raise e


async def handle_get_user_project_by_id(
    db: AsyncSession, current_user: User, user_project_id: UUID
) -> GetUserProjectResponse:
    try:
        user_project = await get_user_project_by_id(db, user_project_id)
        if user_project is None:
            raise NotFoundException()

        return GetUserProjectResponse(
            userProject=UserProjectDTO.model_validate(user_project),
            message="User Project fetched successfully")
    except NotFoundException as e:
        logging.exception("Could not find User Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Project details")
        raise e


async def handle_create_user_project(
    db: AsyncSession, current_user: User, user_project_create: UserProjectCreate
) -> CreateUserProjectResponse:
    try:
        new_user_project = UserProject(
            **user_project_create.model_dump(),
            allocated_by=current_user.user_id,
        )
        created_user_project = await create_user_project(db, new_user_project)
        return CreateUserProjectResponse(
            newUserProject=UserProjectDTO.model_validate(created_user_project),
            message="User Project created successfully")
    except Exception as e:
        logging.exception("Some error occurred while creating User Project")
        raise e


async def handle_update_user_project(
    db: AsyncSession,
    current_user: User,
    user_project_update: UserProjectUpdate,
    user_project_id: UUID,
) -> UpdateUserProjectResponse:
    try:
        update_data = user_project_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data["allocation_updated_by"] = current_user.user_id
        updated_user_project = await update_user_project(db, update_data, user_project_id)
        if updated_user_project is None:
            raise NotFoundException()

        return UpdateUserProjectResponse(
            updatedUserProject=UserProjectDTO.model_validate(updated_user_project),
            message="User Project updated successfully")
    except NotFoundException as e:
        logging.exception("Could not find User Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating User Project")
        raise e


async def handle_delete_user_project(
    db: AsyncSession, current_user: User, user_project_id: UUID
) -> DeleteUserProjectResponse:
    try:
        deleted_user_project = await delete_user_project(db, user_project_id)
        if deleted_user_project is None:
            raise NotFoundException()

        return DeleteUserProjectResponse(
            message="User Project deleted successfully"
        )
    except NotFoundException as e:
        logging.exception("Could not find User Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting User Project")
        raise e