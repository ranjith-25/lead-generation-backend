from app.services.db.job_roles import (
    get_job_roles,
    get_job_role_by_id,
    create_job_role,
    update_job_role,
    delete_job_role,
)
from app.responses.job_roles import (
    GetJobRolesResponse,
    CreateJobRolesResponse,
    UpdateJobRolesResponse,
    DeleteJobRolesResponse,
)
from app.schemas.job_roles import JobRolesCreate, JobRolesUpdate, JobRolesDTO
from app.models.job_roles import JobRoles
from app.models.user import User
from app.exceptions.custom import NotFoundException
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.string_normalizing import normalize_string


async def handle_get_job_roles(db: AsyncSession, current_user: User) -> GetJobRolesResponse:
    try:
        job_roles = await get_job_roles(db)

        if job_roles is None:
            raise NotFoundException()

        job_roles_response = GetJobRolesResponse(
            jobRoleList=[JobRolesDTO.model_validate(job_role) for job_role in job_roles],
            message="Job Roles fetched successfully",
            status_code=200
        )
        return job_roles_response

    except NotFoundException as e:
        logging.exception("Could not find Job Roles")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while getting Job Roles list")
        raise e


async def handle_get_job_role_by_id(db: AsyncSession, current_user: User, job_role_id: int) -> GetJobRolesResponse:
    try:
        job_role_details = await get_job_role_by_id(db, job_role_id)

        if job_role_details is None:
            raise NotFoundException()

        job_role_details_response = GetJobRolesResponse(
            jobRole=JobRolesDTO.model_validate(job_role_details),
            message="Job Role fetched successfully",
            status_code=200
        )

        return job_role_details_response

    except NotFoundException as e:
        logging.exception("Could not find Job Roles")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while getting Job Role details")
        raise e


async def handle_create_job_role(db: AsyncSession, current_user: User, job_role_create: JobRolesCreate) -> CreateJobRolesResponse:
    try:
        new_job_role = JobRoles(
            **job_role_create.model_dump(),
            normalizedName = normalize_string(job_role_create.displayName),
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id
        )
        job_role = await create_job_role(db, new_job_role)
        job_role_response = CreateJobRolesResponse(
            newJobRole=JobRolesDTO.model_validate(job_role),
            message="Job Role created successfully",
            status_code=200
        )

        return job_role_response

    except Exception as e:
        logging.exception("Some error occurred while creating Job Role")
        raise e


async def handle_update_job_role(db: AsyncSession, current_user: User, job_role_update: JobRolesUpdate, job_role_id: int) -> UpdateJobRolesResponse:
    try:
        updated_job_role = job_role_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_job_role["normalizedName"] = normalize_string(job_role_create.displayName),
        updated_job_role["updatedBy"] = current_user.user_id
        job_role = await update_job_role(db, updated_job_role, job_role_id)

        if job_role is None:
            raise NotFoundException()

        job_role_response = UpdateJobRolesResponse(
            updatedJobRole=JobRolesDTO.model_validate(job_role),
            message="Job Role updated successfully",
            status_code=200
        )

        return job_role_response

    except NotFoundException as e:
        logging.exception("Could not find Job Role")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while updating Job Role")
        raise e


async def handle_delete_job_role(db: AsyncSession, current_user: User, job_role_id: int) -> DeleteJobRolesResponse:
    try:
        job_role_details = await delete_job_role(db, job_role_id)

        if job_role_details is None:
            raise NotFoundException()

        job_role_details_response = DeleteJobRolesResponse(
            message="Job Role deleted successfully",
            status_code=200
        )
        return job_role_details_response

    except NotFoundException as e:
        logging.exception("Could not find Job Roles")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while deleting Job Role")
        raise e
