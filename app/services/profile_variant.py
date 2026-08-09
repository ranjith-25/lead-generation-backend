import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.exceptions.custom import NotFoundException
from app.models.profile_variant import ProfileVariant
from app.models.user import User
from app.responses.profile_variant import (
    CreateProfileVariantResponse,
    DeleteProfileVariantResponse,
    GetProfileVariantResponse,
    UpdateProfileVariantResponse,
)
from app.schemas.profile_variant import ProfileVariantCreate, ProfileVariantDTO, ProfileVariantUpdate
from app.services.db.profile_variant import (
    create_profile_variant,
    delete_profile_variant,
    get_all_profile_variants,
    get_profile_variant_by_id,
    update_profile_variant,
)


async def handle_get_all_profile_variants(db: AsyncSession, current_user: User) -> GetProfileVariantResponse:
    try:
        profile_variants = await get_all_profile_variants(db)
        if profile_variants is None:
            raise NotFoundException()

        return GetProfileVariantResponse(
            profileVariantList=[ProfileVariantDTO.model_validate(pv) for pv in profile_variants],
            message="Profile Variants fetched successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variants")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Profile Variants list")
        raise e


async def handle_get_profile_variant_by_id(db: AsyncSession, current_user: User, profile_variant_id: UUID) -> GetProfileVariantResponse:
    try:
        profile_variant = await get_profile_variant_by_id(db, profile_variant_id)
        if profile_variant is None:
            raise NotFoundException()

        return GetProfileVariantResponse(
            profileVariant=ProfileVariantDTO.model_validate(profile_variant),
            message="Profile Variant fetched successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Profile Variant details")
        raise e


async def handle_create_profile_variant(
    db: AsyncSession, current_user: User, profile_variant_create: ProfileVariantCreate
) -> CreateProfileVariantResponse:
    try:
        create_data = profile_variant_create.model_dump(exclude={"projects"})
        new_profile_variant = ProfileVariant(
            **create_data,
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
        )
        created_profile_variant = await create_profile_variant(
            db, new_profile_variant, profile_variant_create.projects or []
        )
        return CreateProfileVariantResponse(
            newProfileVariant=ProfileVariantDTO.model_validate(created_profile_variant),
            message="Profile Variant created successfully",
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Profile Variant")
        raise e


async def handle_update_profile_variant(
    db: AsyncSession, current_user: User, profile_variant_update: ProfileVariantUpdate, profile_variant_id: UUID
) -> UpdateProfileVariantResponse:
    try:
        update_data = profile_variant_update.model_dump(exclude={"projects"}, exclude_unset=True, exclude_none=True)
        update_data["updated_by"] = current_user.user_id
        
        updated_profile_variant = await update_profile_variant(
            db, update_data, profile_variant_update.projects, profile_variant_id
        )
        if updated_profile_variant is None:
            raise NotFoundException()

        return UpdateProfileVariantResponse(
            updatedProfileVariant=ProfileVariantDTO.model_validate(updated_profile_variant),
            message="Profile Variant updated successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Profile Variant")
        raise e


async def handle_delete_profile_variant(
    db: AsyncSession, current_user: User, profile_variant_id: UUID
) -> DeleteProfileVariantResponse:
    try:
        deleted_profile_variant = await delete_profile_variant(db, profile_variant_id)
        if deleted_profile_variant is None:
            raise NotFoundException()

        return DeleteProfileVariantResponse(
            message="Profile Variant deleted successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Profile Variant")
        raise e