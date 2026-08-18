import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import LogAction
from app.exceptions.custom import NotFoundException
from app.models.pipeline_opportunity_project import PipelineOpportunityProjectModel
from app.models.user import User
from app.responses.pipeline_opportunity_project import (
    CreatePipelineOpportunityProjectResponse,
    DeletePipelineOpportunityProjectResponse,
    GetPipelineOpportunityProjectResponse,
    UpdatePipelineOpportunityProjectResponse,
)
from app.schemas.pipeline_opportunity_project import (
    PipelineOpportunityProjectCreate,
    PipelineOpportunityProjectDTO,
    PipelineOpportunityProjectUpdate,
)
from app.services.db.pipeline_opportunity_project import (
    create_pipeline_opportunity_project,
    delete_pipeline_opportunity_project,
    get_all_pipeline_opportunity_projects,
    get_pipeline_opportunity_project_by_id,
    update_pipeline_opportunity_project,
    get_pipeline_opportunity_project_by_opportunity_id
)
from app.services.system_log import log_activity


async def handle_get_all_pipeline_opportunity_projects(
    db: AsyncSession, current_user: User, page: int = 1, limit: int = 10
) -> GetPipelineOpportunityProjectResponse:
    try:
        pipeline_opportunity_projects, total = await get_all_pipeline_opportunity_projects(db, page, limit)

        return GetPipelineOpportunityProjectResponse(
            pipelineOpportunityProjectList=[
                PipelineOpportunityProjectDTO.model_validate(project) for project in pipeline_opportunity_projects
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Pipeline Opportunity Projects fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Projects")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Projects list")
        raise e


async def handle_get_pipeline_opportunity_project_by_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_project_id: UUID
) -> GetPipelineOpportunityProjectResponse:
    try:
        pipeline_opportunity_project = await get_pipeline_opportunity_project_by_id(db, pipeline_opportunity_project_id)
        if pipeline_opportunity_project is None:
            raise NotFoundException()

        return GetPipelineOpportunityProjectResponse(
            pipelineOpportunityProject=PipelineOpportunityProjectDTO.model_validate(pipeline_opportunity_project),
            message="Pipeline Opportunity Project fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Project details")
        raise e


async def handle_get_pipeline_opportunity_project_by_opportunity_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_id: UUID
) -> GetPipelineOpportunityProjectResponse:
    try:
        pipeline_opportunity_projects = await get_pipeline_opportunity_project_by_opportunity_id(db, pipeline_opportunity_id)

        return GetPipelineOpportunityProjectResponse(
            pipelineOpportunityProjectList=[PipelineOpportunityProjectDTO.model_validate(project) for project in pipeline_opportunity_projects],
            message="Pipeline Opportunity Project fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Project details")
        raise e


async def handle_create_pipeline_opportunity_project(
    db: AsyncSession, current_user: User, pipeline_opportunity_project_create: PipelineOpportunityProjectCreate
) -> CreatePipelineOpportunityProjectResponse:
    try:
        create_data = pipeline_opportunity_project_create.model_dump()
        create_data.pop("is_active", None)
        new_pipeline_opportunity_project = PipelineOpportunityProjectModel(
            **create_data,
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        await log_activity(
            db,
            LogAction.PIPELINE_PROJECT_CREATED,
            current_user,
            entity_type="pipeline_project",
            entity_name=new_pipeline_opportunity_project.project_name,
            details={
                "opportunity_id": create_data.get("opportunity_id"),
                "project_id": create_data.get("project_id"),
                "match_score": create_data.get("match_score"),
            },
        )
        created_pipeline_opportunity_project = await create_pipeline_opportunity_project(db, new_pipeline_opportunity_project)
        return CreatePipelineOpportunityProjectResponse(
            newPipelineOpportunityProject=PipelineOpportunityProjectDTO.model_validate(created_pipeline_opportunity_project),
            message="Pipeline Opportunity Project created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Pipeline Opportunity Project")
        raise e


async def handle_update_pipeline_opportunity_project(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_project_update: PipelineOpportunityProjectUpdate,
    pipeline_opportunity_project_id: UUID,
) -> UpdatePipelineOpportunityProjectResponse:
    try:
        update_data = pipeline_opportunity_project_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("is_active", None)
        update_data["updatedBy"] = current_user.user_id
        await log_activity(
            db,
            LogAction.PIPELINE_PROJECT_UPDATED,
            current_user,
            entity_type="pipeline_project",
            entity_id=pipeline_opportunity_project_id,
            entity_name=update_data.get("project_name"),
            details={"updated_fields": [key for key in update_data if key != "updatedBy"]},
        )
        updated_pipeline_opportunity_project = await update_pipeline_opportunity_project(
            db, update_data, pipeline_opportunity_project_id
        )
        if updated_pipeline_opportunity_project is None:
            raise NotFoundException()

        return UpdatePipelineOpportunityProjectResponse(
            updatedPipelineOpportunityProject=PipelineOpportunityProjectDTO.model_validate(updated_pipeline_opportunity_project),
            message="Pipeline Opportunity Project updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Pipeline Opportunity Project")
        raise e


async def handle_delete_pipeline_opportunity_project(
    db: AsyncSession, current_user: User, pipeline_opportunity_project_id: UUID
) -> DeletePipelineOpportunityProjectResponse:
    try:
        # Read while the row still exists so the log keeps its name/context after the delete.
        pipeline_opportunity_project = await get_pipeline_opportunity_project_by_id(db, pipeline_opportunity_project_id)
        if pipeline_opportunity_project is not None:
            await log_activity(
                db,
                LogAction.PIPELINE_PROJECT_DELETED,
                current_user,
                entity_type="pipeline_project",
                entity_id=pipeline_opportunity_project.id,
                entity_name=pipeline_opportunity_project.project_name,
                details={
                    "opportunity_id": pipeline_opportunity_project.opportunity_id,
                    "project_id": pipeline_opportunity_project.project_id,
                },
            )

        deleted_pipeline_opportunity_project = await delete_pipeline_opportunity_project(db, pipeline_opportunity_project_id)
        if deleted_pipeline_opportunity_project is None:
            raise NotFoundException()

        return DeletePipelineOpportunityProjectResponse(
            message="Pipeline Opportunity Project deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Pipeline Opportunity Project")
        raise e
