import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
from app.exceptions.custom import NotFoundException
from app.models.pipeline_opportunity_techincal_preperation import PipelineOpportunityTechnicalPreperationModel
from app.models.user import User
from app.responses.pipeline_opportunity_techincal_preperation import (
    CreatePipelineOpportunityTechnicalPreperationResponse,
    DeletePipelineOpportunityTechnicalPreperationResponse,
    GetPipelineOpportunityTechnicalPreperationResponse,
    UpdatePipelineOpportunityTechnicalPreperationResponse,
)
from app.schemas.pipeline_opportunity_techincal_preperation import (
    PipelineOpportunityTechnicalPreperationCreate,
    PipelineOpportunityTechnicalPreperationDTO,
    PipelineOpportunityTechnicalPreperationUpdate,
)
from app.services.db.pipeline_opportunity_techincal_preperation import (
    create_pipeline_opportunity_technical_preperation,
    delete_pipeline_opportunity_technical_preperation,
    get_all_pipeline_opportunity_technical_preperations,
    get_pipeline_opportunity_technical_preperation_by_id,
    update_pipeline_opportunity_technical_preperation,
    get_pipeline_opportunity_technical_preperation_by_opportunity_id
)


async def handle_get_all_pipeline_opportunity_technical_preperations(
    db: AsyncSession, current_user: User, page: int = 1, limit: int = 10
) -> GetPipelineOpportunityTechnicalPreperationResponse:
    try:
        pipeline_opportunity_technical_preperations, total = await get_all_pipeline_opportunity_technical_preperations(db, page, limit)

        return GetPipelineOpportunityTechnicalPreperationResponse(
            pipelineOpportunityTechnicalPreperationList=[
                PipelineOpportunityTechnicalPreperationDTO.model_validate(prep) for prep in pipeline_opportunity_technical_preperations
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Pipeline Opportunity Technical Preperations fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Technical Preperations")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Technical Preperations list")
        raise e


async def handle_get_pipeline_opportunity_technical_preperation_by_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_technical_preperation_id: UUID
) -> GetPipelineOpportunityTechnicalPreperationResponse:
    try:
        pipeline_opportunity_technical_preperation = await get_pipeline_opportunity_technical_preperation_by_id(db, pipeline_opportunity_technical_preperation_id)
        if pipeline_opportunity_technical_preperation is None:
            raise NotFoundException()

        return GetPipelineOpportunityTechnicalPreperationResponse(
            pipelineOpportunityTechnicalPreperation=PipelineOpportunityTechnicalPreperationDTO.model_validate(pipeline_opportunity_technical_preperation),
            message="Pipeline Opportunity Technical Preperation fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Technical Preperation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Technical Preperation details")
        raise e


async def handle_get_pipeline_opportunity_technical_preperation_by_opportunity_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_id: UUID
) -> GetPipelineOpportunityTechnicalPreperationResponse:
    try:
        pipeline_opportunity_technical_preperations = await get_pipeline_opportunity_technical_preperation_by_opportunity_id(db, pipeline_opportunity_id)

        return GetPipelineOpportunityTechnicalPreperationResponse(
            pipelineOpportunityTechnicalPreperationList=[PipelineOpportunityTechnicalPreperationDTO.model_validate(prep) for prep in pipeline_opportunity_technical_preperations],
            message="Pipeline Opportunity Technical Preperation fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Technical Preperation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Technical Preperation details")
        raise e


async def handle_create_pipeline_opportunity_technical_preperation(
    db: AsyncSession, current_user: User, pipeline_opportunity_technical_preperation_create: PipelineOpportunityTechnicalPreperationCreate
) -> CreatePipelineOpportunityTechnicalPreperationResponse:
    try:
        create_data = pipeline_opportunity_technical_preperation_create.model_dump()
        create_data.pop("is_active", None)
        new_pipeline_opportunity_technical_preperation = PipelineOpportunityTechnicalPreperationModel(
            **create_data,
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        created_pipeline_opportunity_technical_preperation = await create_pipeline_opportunity_technical_preperation(db, new_pipeline_opportunity_technical_preperation)
        return CreatePipelineOpportunityTechnicalPreperationResponse(
            newPipelineOpportunityTechnicalPreperation=PipelineOpportunityTechnicalPreperationDTO.model_validate(created_pipeline_opportunity_technical_preperation),
            message="Pipeline Opportunity Technical Preperation created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Pipeline Opportunity Technical Preperation")
        raise e


async def handle_update_pipeline_opportunity_technical_preperation(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_technical_preperation_update: PipelineOpportunityTechnicalPreperationUpdate,
    pipeline_opportunity_technical_preperation_id: UUID,
) -> UpdatePipelineOpportunityTechnicalPreperationResponse:
    try:
        update_data = pipeline_opportunity_technical_preperation_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("is_active", None)
        update_data["updatedBy"] = current_user.user_id
        updated_pipeline_opportunity_technical_preperation = await update_pipeline_opportunity_technical_preperation(
            db, update_data, pipeline_opportunity_technical_preperation_id
        )
        if updated_pipeline_opportunity_technical_preperation is None:
            raise NotFoundException()

        return UpdatePipelineOpportunityTechnicalPreperationResponse(
            updatedPipelineOpportunityTechnicalPreperation=PipelineOpportunityTechnicalPreperationDTO.model_validate(updated_pipeline_opportunity_technical_preperation),
            message="Pipeline Opportunity Technical Preperation updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Technical Preperation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Pipeline Opportunity Technical Preperation")
        raise e


async def handle_delete_pipeline_opportunity_technical_preperation(
    db: AsyncSession, current_user: User, pipeline_opportunity_technical_preperation_id: UUID
) -> DeletePipelineOpportunityTechnicalPreperationResponse:
    try:
        deleted_pipeline_opportunity_technical_preperation = await delete_pipeline_opportunity_technical_preperation(db, pipeline_opportunity_technical_preperation_id)
        if deleted_pipeline_opportunity_technical_preperation is None:
            raise NotFoundException()

        return DeletePipelineOpportunityTechnicalPreperationResponse(
            message="Pipeline Opportunity Technical Preperation deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Technical Preperation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Pipeline Opportunity Technical Preperation")
        raise e

async def handle_update_pipeline_opportunity_technical_preperation_comments(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_technical_preperation_comments: list[str],
    pipeline_opportunity_technical_preperation_id: UUID,
) -> UpdatePipelineOpportunityTechnicalPreperationResponse:
    try:
        update_data = {"comments" : pipeline_opportunity_technical_preperation_comments, "updatedBy" : current_user.user_id}
        updated_pipeline_opportunity_technical_preperation = await update_pipeline_opportunity_technical_preperation(
            db, update_data, pipeline_opportunity_technical_preperation_id
        )
        if updated_pipeline_opportunity_technical_preperation is None:
            raise NotFoundException()

        return UpdatePipelineOpportunityTechnicalPreperationResponse(
            updatedPipelineOpportunityTechnicalPreperation=PipelineOpportunityTechnicalPreperationDTO.model_validate(updated_pipeline_opportunity_technical_preperation),
            message="Pipeline Opportunity Technical Preperation updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Technical Preperation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Pipeline Opportunity Technical Preperation")
        raise e