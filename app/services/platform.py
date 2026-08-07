import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.models.platform import Platform
from app.models.user import User
from app.responses.platform import (
    CreatePlatformResponse,
    DeletePlatformResponse,
    GetPlatformResponse,
    UpdatePlatformResponse,
)
from app.schemas.platform import PlatformCreate, PlatformDTO, PlatformUpdate, PlatformListRead
from app.services.db.platform import (
    create_platform,
    delete_platform,
    get_all_platforms,
    get_platform_by_id,
    update_platform,
)


async def handle_get_all_platforms(db: AsyncSession, current_user: User, search: str | None = None, page: int = 1, limit: int = 10) -> GetPlatformResponse:
    try:
        platforms, total = await get_all_platforms(db, search, page, limit)
        return GetPlatformResponse(
            platformList=[PlatformListRead.model_validate(p) for p in platforms],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Platform list fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Platforms")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Platforms list")
        raise e


async def handle_get_platform_by_id(db: AsyncSession, current_user: User, platform_id: int) -> GetPlatformResponse:
    try:
        platform = await get_platform_by_id(db, platform_id)
        if platform is None:
            raise NotFoundException()

        return GetPlatformResponse(
            platform=PlatformDTO.model_validate(platform),
            message="Platform fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Platform")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Platform details")
        raise e


async def handle_create_platform(
    db: AsyncSession, current_user: User, platform_create: PlatformCreate
) -> CreatePlatformResponse:
    try:
        new_platform = Platform(**platform_create.model_dump())
        created_platform = await create_platform(db, new_platform)
        return CreatePlatformResponse(
            newPlatform=PlatformDTO.model_validate(created_platform),
            message="Platform created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Platform")
        raise e


async def handle_update_platform(
    db: AsyncSession, current_user: User, platform_update: PlatformUpdate, platform_id: int
) -> UpdatePlatformResponse:
    try:
        update_data = platform_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_platform = await update_platform(db, update_data, platform_id)
        if updated_platform is None:
            raise NotFoundException()

        return UpdatePlatformResponse(
            updatedPlatform=PlatformDTO.model_validate(updated_platform),
            message="Platform updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Platform")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Platform")
        raise e


async def handle_delete_platform(
    db: AsyncSession, current_user: User, platform_id: int
) -> DeletePlatformResponse:
    try:
        deleted_platform = await delete_platform(db, platform_id)
        if deleted_platform is None:
            raise NotFoundException()

        return DeletePlatformResponse(
            message="Platform deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Platform")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Platform")
        raise e
