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
    UserProjectConfigurationsData,
    UserProjectConfigurationsResponse,
)
from app.schemas.user_project import (
    ProjectInfo,
    RoleInfo,
    TechStackInfo,
    UserProjectCreate,
    UserProjectDTO,
    UserProjectDetailDTO,
    UserProjectUpdate,
)
from app.services.db.user_project import (
    create_user_project,
    delete_user_project,
    get_all_user_projects,
    get_user_project_by_id,
    get_user_project_configurations,
    update_user_project,
)


async def handle_get_user_project_configurations(
    db: AsyncSession, current_user: User
) -> UserProjectConfigurationsResponse:
    try:
        projects, roles, techstacks = await get_user_project_configurations(db)

        return UserProjectConfigurationsResponse(
            data=UserProjectConfigurationsData(
                projects=list(projects),
                roles=list(roles),
                techstacks=list(techstacks),
            ),
            message="User Project configurations fetched successfully",
        )
    except Exception as e:
        logging.exception("Some error occurred while getting User Project configurations")
        raise e


def _to_detail_dto(row) -> UserProjectDetailDTO:
    """Map a (UserProject, project_name, role_name, techstack_name) row to the read DTO."""

    user_project, project_name, role_name, techstack_name = row

    return UserProjectDetailDTO(
        project=ProjectInfo(
            project_id=user_project.project_id,
            project_name=project_name,
        ),
        role=RoleInfo(
            role_id=user_project.role_id,
            role_name=role_name,
        ),
        techstack=TechStackInfo(
            techstack_id=user_project.techstack_id,
            techstack_name=techstack_name,
        ),
        user_id=user_project.user_id,
        user_project_id=user_project.user_project_id,
        allocated_by=user_project.allocated_by,
        allocation_updated_by=user_project.allocation_updated_by,
        created_at=user_project.created_at,
        updated_at=user_project.updated_at,
    )


async def handle_search_user_projects(
    db: AsyncSession, current_user: User, user_id: UUID | None = None
) -> GetUserProjectResponse:
    try:
        user_projects = await get_all_user_projects(db, user_id)

        return GetUserProjectResponse(
            userProjectList=[_to_detail_dto(row) for row in user_projects],
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
            userProject=_to_detail_dto(user_project),
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