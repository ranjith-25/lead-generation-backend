import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel
from app.models.user import User
from app.responses.pipeline_opportunity_resource import (
    CreatePipelineOpportunityResourceResponse,
    DeletePipelineOpportunityResourceResponse,
    GetPipelineOpportunityResourceResponse,
    UpdatePipelineOpportunityResourceResponse,
)
from app.schemas.pipeline_opportunity_resource import (
    PipelineOpportunityResourceCreate,
    PipelineOpportunityResourceDTO,
    PipelineOpportunityResourceUpdate,
)
from app.services.db.pipeline_opportunity_resource import (
    create_pipeline_opportunity_resource,
    delete_pipeline_opportunity_resource,
    get_all_pipeline_opportunity_resources,
    get_pipeline_opportunity_resource_by_id,
    update_pipeline_opportunity_resource,
    get_pipeline_opportunity_resource_by_opportunity_id
)


async def handle_get_all_pipeline_opportunity_resources(
    db: AsyncSession, current_user: User, page: int = 1, limit: int = 10
) -> GetPipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resources, total = await get_all_pipeline_opportunity_resources(db, page, limit)

        return GetPipelineOpportunityResourceResponse(
            pipelineOpportunityResourceList=[
                PipelineOpportunityResourceDTO.model_validate(resource) for resource in pipeline_opportunity_resources
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Pipeline Opportunity Resources fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resources")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Resources list")
        raise e


async def handle_get_pipeline_opportunity_resource_by_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_resource_id: UUID
) -> GetPipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resource = await get_pipeline_opportunity_resource_by_id(db, pipeline_opportunity_resource_id)
        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        return GetPipelineOpportunityResourceResponse(
            pipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(pipeline_opportunity_resource),
            message="Pipeline Opportunity Resource fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Resource details")
        raise e


async def handle_get_pipeline_opportunity_resource_by_opportunity_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_id: UUID
) -> GetPipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resources = await get_pipeline_opportunity_resource_by_opportunity_id(db, pipeline_opportunity_id)

        return GetPipelineOpportunityResourceResponse(
            pipelineOpportunityResourceList=[PipelineOpportunityResourceDTO.model_validate(resource) for resource in pipeline_opportunity_resources],
            message="Pipeline Opportunity Resource fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Resource details")
        raise e


async def handle_create_pipeline_opportunity_resource(
    db: AsyncSession, current_user: User, pipeline_opportunity_resource_create: PipelineOpportunityResourceCreate
) -> CreatePipelineOpportunityResourceResponse:
    try:
        create_data = pipeline_opportunity_resource_create.model_dump()
        create_data.pop("is_active", None)
        new_pipeline_opportunity_resource = PipelineOpportunityResourceModel(
            **create_data,
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        created_pipeline_opportunity_resource = await create_pipeline_opportunity_resource(db, new_pipeline_opportunity_resource)
        return CreatePipelineOpportunityResourceResponse(
            newPipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(created_pipeline_opportunity_resource),
            message="Pipeline Opportunity Resource created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Pipeline Opportunity Resource")
        raise e


async def handle_update_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource_update: PipelineOpportunityResourceUpdate,
    pipeline_opportunity_resource_id: UUID,
) -> UpdatePipelineOpportunityResourceResponse:
    try:
        update_data = pipeline_opportunity_resource_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("is_active", None)
        update_data["updatedBy"] = current_user.user_id
        updated_pipeline_opportunity_resource = await update_pipeline_opportunity_resource(
            db, update_data, pipeline_opportunity_resource_id
        )
        if updated_pipeline_opportunity_resource is None:
            raise NotFoundException()

        return UpdatePipelineOpportunityResourceResponse(
            updatedPipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(updated_pipeline_opportunity_resource),
            message="Pipeline Opportunity Resource updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Pipeline Opportunity Resource")
        raise e


async def handle_delete_pipeline_opportunity_resource(
    db: AsyncSession, current_user: User, pipeline_opportunity_resource_id: UUID
) -> DeletePipelineOpportunityResourceResponse:
    try:
        deleted_pipeline_opportunity_resource = await delete_pipeline_opportunity_resource(db, pipeline_opportunity_resource_id)
        if deleted_pipeline_opportunity_resource is None:
            raise NotFoundException()

        return DeletePipelineOpportunityResourceResponse(
            message="Pipeline Opportunity Resource deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Pipeline Opportunity Resource")
        raise e