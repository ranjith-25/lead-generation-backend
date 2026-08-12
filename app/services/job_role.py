import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.custom import NotFoundException
from app.models.job_role import JobRole
from app.models.user import User
from app.responses.job_role import (
    CreateJobRoleResponse,
    DeleteJobRoleResponse,
    GetJobRoleResponse,
    UpdateJobRoleResponse,
)
from app.schemas.job_role import JobRoleCreate, JobRoleDTO, JobRoleUpdate
from app.services.db.job_role import (
    create_job_role,
    delete_job_role,
    get_all_job_roles,
    get_job_role_by_id,
    update_job_role,
)
from app.services.db.user import (
    getAllUsers
)
from app.schemas.job_role import JobRoleFilters

async def handle_get_all_job_roles(db: AsyncSession, page: int = 0, limit : int | None = None) -> GetJobRoleResponse: 
    try:
        job_roles = await get_all_job_roles(db, JobRoleFilters(page = page, limit=limit))
        if job_roles is None:
            raise NotFoundException()

        all_users = await getAllUsers(db)
        for job_role in job_roles:
            count = 0
            for all_user in all_users:
                if all_user.role_id == job_role.id:
                    count += 1
            job_role.user_count = count
            
        return GetJobRoleResponse(
            jobRoleList=[JobRoleDTO.model_validate(role) for role in job_roles],
            message="Job Roles fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Job Roles")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Job Roles list")
        raise e


async def handle_get_job_role_by_id(db: AsyncSession, current_user: User, job_role_id: UUID) -> GetJobRoleResponse:
    try:
        job_role = await get_job_role_by_id(db, job_role_id)
        if job_role is None:
            raise NotFoundException()

        return GetJobRoleResponse(
            jobRole=JobRoleDTO.model_validate(job_role),
            message="Job Role fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Job Role")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Job Role details")
        raise e


async def handle_create_job_role(
    db: AsyncSession, current_user: User, job_role_create: JobRoleCreate
) -> CreateJobRoleResponse:
    try:
        new_job_role = JobRole(
            **job_role_create.model_dump(),
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        created_job_role = await create_job_role(db, new_job_role)
        return CreateJobRoleResponse(
            newJobRole=JobRoleDTO.model_validate(created_job_role),
            message="Job Role created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Job Role")
        raise e


async def handle_update_job_role(
    db: AsyncSession, current_user: User, job_role_update: JobRoleUpdate, job_role_id: UUID
) -> UpdateJobRoleResponse:
    try:
        update_data = job_role_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updatedBy"] = current_user.user_id
        updated_job_role = await update_job_role(db, update_data, job_role_id)
        if updated_job_role is None:
            raise NotFoundException()

        return UpdateJobRoleResponse(
            updatedJobRole=JobRoleDTO.model_validate(updated_job_role),
            message="Job Role updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Job Role")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Job Role")
        raise e


async def handle_delete_job_role(
    db: AsyncSession, current_user: User, job_role_id: UUID
) -> DeleteJobRoleResponse:
    try:
        deleted_job_role = await delete_job_role(db, job_role_id)
        if deleted_job_role is None:
            raise NotFoundException()

        return DeleteJobRoleResponse(
            message="Job Role deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Job Role")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Job Role")
        raise e
