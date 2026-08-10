import logging

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode
from app.exceptions.project import TechStackNotFoundException
from app.models.techstacks import TechStacks
from app.models.user import User
from app.responses.techstack import (
    CreateTechStackResponse,
    DeleteTechStackResponse,
    GetTechStackResponse,
    UpdateTechStackResponse,
)
from app.schemas.techstack import TechStackCreate, TechStackDTO, TechStackUpdate, TechstackFilters
from app.services.db.techstack import (
    add_techstack_db,
    delete_techstack_db,
    get_all_techstacks_db,
    get_techstack_by_id_db,
    get_techstack_by_name_db,
    update_techstack_db,
)


def _techstack_already_exists() -> AppException:
    return AppException(
        message="A tech stack with this name already exists",
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorCode.DUPLICATE_RECORD,
    )


async def handle_get_techstacks(db: AsyncSession, current_user: User, page: int, limit : int) -> GetTechStackResponse:
    try:
        techstacks = await get_all_techstacks_db(db, TechstackFilters(page=page, limit=limit))

        return GetTechStackResponse(
            techStackList=[TechStackDTO.model_validate(techstack) for techstack in techstacks],
            message="Tech Stacks fetched successfully",
        )

    except Exception as e:
        logging.exception("Some error occurred while getting Tech Stacks list")
        raise e


async def handle_get_techstack_by_id(
    db: AsyncSession, current_user: User, techstack_id: UUID
) -> GetTechStackResponse:
    try:
        techstack = await get_techstack_by_id_db(db, techstack_id)

        if techstack is None:
            raise TechStackNotFoundException([techstack_id])

        return GetTechStackResponse(
            techStack=TechStackDTO.model_validate(techstack),
            message="Tech Stack fetched successfully",
        )

    except TechStackNotFoundException as e:
        logging.exception("Could not find Tech Stack")
        raise e

    except Exception as e:
        logging.exception("Some error occurred while getting Tech Stack details")
        raise e


async def handle_create_techstack(
    db: AsyncSession, current_user: User, techstack_create: TechStackCreate
) -> CreateTechStackResponse:
    try:
        existing = await get_techstack_by_name_db(db, techstack_create.techstack_name)
        if existing:
            raise _techstack_already_exists()

        new_techstack = TechStacks(
            **techstack_create.model_dump(),
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        techstack = await add_techstack_db(db, new_techstack)

        return CreateTechStackResponse(
            newTechStack=TechStackDTO.model_validate(techstack),
            message="Tech Stack created successfully",
        )

    except AppException as e:
        raise e

    except Exception as e:
        logging.exception("Some error occurred while creating Tech Stack")
        raise e


async def handle_update_techstack(
    db: AsyncSession, current_user: User, techstack_update: TechStackUpdate, techstack_id: UUID
) -> UpdateTechStackResponse:
    try:
        techstack = await get_techstack_by_id_db(db, techstack_id)

        if techstack is None:
            raise TechStackNotFoundException([techstack_id])

        update_data = techstack_update.model_dump(exclude_unset=True, exclude_none=True)

        if "techstack_name" in update_data:
            existing = await get_techstack_by_name_db(db, update_data["techstack_name"])
            if existing and existing.techstack_id != techstack_id:
                raise _techstack_already_exists()

        update_data["updatedBy"] = current_user.user_id

        updated_techstack = await update_techstack_db(db, techstack, update_data)

        return UpdateTechStackResponse(
            updatedTechStack=TechStackDTO.model_validate(updated_techstack),
            message="Tech Stack updated successfully",
        )

    except AppException as e:
        raise e

    except Exception as e:
        logging.exception("Some error occurred while updating Tech Stack")
        raise e


async def handle_delete_techstack(
    db: AsyncSession, current_user: User, techstack_id: UUID
) -> DeleteTechStackResponse:
    try:
        techstack = await get_techstack_by_id_db(db, techstack_id)

        if techstack is None:
            raise TechStackNotFoundException([techstack_id])

        await delete_techstack_db(db, techstack)

        return DeleteTechStackResponse(
            message="Tech Stack deleted successfully",
        )

    except AppException as e:
        raise e

    except Exception as e:
        logging.exception("Some error occurred while deleting Tech Stack")
        raise e
