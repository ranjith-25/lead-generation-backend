import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.models.pipeline_execution_status import PipelineExecutionStatusModel
from app.models.user import User
from app.responses.pipeline_execution_status import (
    CreatePipelineExecutionStatusResponse,
    DeletePipelineExecutionStatusResponse,
    GetPipelineExecutionStatusResponse,
    UpdatePipelineExecutionStatusResponse,
)
from app.schemas.pipeline_execution_status import (
    PipelineExecutionStatusCreate,
    PipelineExecutionStatusDTO,
    PipelineExecutionStatusUpdate,
)
from app.services.db.pipeline_execution_status import (
    create_pipeline_execution_status,
    delete_pipeline_execution_status,
    get_all_pipeline_execution_statuses,
    get_pipeline_execution_status_by_id,
    update_pipeline_execution_status,
    get_pipeline_execution_status_by_opportunity_id
)


async def handle_get_all_pipeline_execution_statuses(
    db: AsyncSession, current_user: User, page: int = 1, limit: int = 10
) -> GetPipelineExecutionStatusResponse:
    try:
        pipeline_execution_statuses, total = await get_all_pipeline_execution_statuses(db, page, limit)

        return GetPipelineExecutionStatusResponse(
            pipelineExecutionStatusList=[
                PipelineExecutionStatusDTO.model_validate(status) for status in pipeline_execution_statuses
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Pipeline Execution Statuses fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Execution Statuses")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Execution Statuses list")
        raise e


async def handle_get_pipeline_execution_status_by_id(
    db: AsyncSession, current_user: User, pipeline_execution_status_id: UUID
) -> GetPipelineExecutionStatusResponse:
    try:
        pipeline_execution_status = await get_pipeline_execution_status_by_id(db, pipeline_execution_status_id)
        if pipeline_execution_status is None:
            raise NotFoundException()

        return GetPipelineExecutionStatusResponse(
            pipelineExecutionStatus=PipelineExecutionStatusDTO.model_validate(pipeline_execution_status),
            message="Pipeline Execution Status fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Execution Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Execution Status details")
        raise e


async def handle_get_pipeline_execution_status_by_opportunity_id(
    db: AsyncSession, current_user: User, opportunity_id: UUID
) -> GetPipelineExecutionStatusResponse:
    try:
        pipeline_execution_status = await get_pipeline_execution_status_by_opportunity_id(db, opportunity_id)
        if pipeline_execution_status is None:
            raise NotFoundException()

        return GetPipelineExecutionStatusResponse(
            pipelineExecutionStatus=PipelineExecutionStatusDTO.model_validate(pipeline_execution_status),
            message="Pipeline Execution Status fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Execution Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Execution Status details")
        raise e


async def handle_create_pipeline_execution_status(
    db: AsyncSession, current_user: User, pipeline_execution_status_create: PipelineExecutionStatusCreate
) -> CreatePipelineExecutionStatusResponse:
    try:
        create_data = pipeline_execution_status_create.model_dump()
        create_data.pop("is_active", None)
        new_pipeline_execution_status = PipelineExecutionStatusModel(**create_data)
        created_pipeline_execution_status = await create_pipeline_execution_status(db, new_pipeline_execution_status)
        return CreatePipelineExecutionStatusResponse(
            newPipelineExecutionStatus=PipelineExecutionStatusDTO.model_validate(created_pipeline_execution_status),
            message="Pipeline Execution Status created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Pipeline Execution Status")
        raise e


async def handle_update_pipeline_execution_status(
    db: AsyncSession,
    current_user: User,
    pipeline_execution_status_update: PipelineExecutionStatusUpdate,
    pipeline_execution_status_id: UUID,
) -> UpdatePipelineExecutionStatusResponse:
    try:
        update_data = pipeline_execution_status_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_pipeline_execution_status = await update_pipeline_execution_status(
            db, update_data, pipeline_execution_status_id
        )
        if updated_pipeline_execution_status is None:
            raise NotFoundException()

        return UpdatePipelineExecutionStatusResponse(
            updatedPipelineExecutionStatus=PipelineExecutionStatusDTO.model_validate(updated_pipeline_execution_status),
            message="Pipeline Execution Status updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Execution Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Pipeline Execution Status")
        raise e


async def handle_delete_pipeline_execution_status(
    db: AsyncSession, current_user: User, pipeline_execution_status_id: UUID
) -> DeletePipelineExecutionStatusResponse:
    try:
        deleted_pipeline_execution_status = await delete_pipeline_execution_status(db, pipeline_execution_status_id)
        if deleted_pipeline_execution_status is None:
            raise NotFoundException()

        return DeletePipelineExecutionStatusResponse(
            message="Pipeline Execution Status deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Execution Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Pipeline Execution Status")
        raise e
