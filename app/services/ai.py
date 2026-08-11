import asyncio
import json
import logging
from time import perf_counter
from uuid import UUID

import httpx
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.ai_connection import get_ai_client
from app.core.connections.postgres import AsyncSessionLocal
from app.exceptions.ai_exception import handle_ai_exception
from app.models.opportunity import Opportunity
from app.models.pipeline_execution_status import PipelineExecutionStatusModel
from app.models.pipeline_opportunity_project import PipelineOpportunityProjectModel
from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel
from app.models.sales_enablement import SalesEnablement
from app.responses.ai import (
    AISalesEnablementResponse,
    GetMatchedProfilesResponse,
    GetRelaventProjectResponse,
    GetScrapedURLDataResponse,
)
from app.responses.opportunity import CreateOpportunityResponse
from app.schemas.ai import AIGetRelaventProfilesRequest , AIManualJDRequest
from app.schemas.opportunity import OpportunityBase
from app.schemas.project import AIProjectRequest
from app.schemas.pipeline_execution_status import (
    PipelineExecutionStatus,
    PipelineExecutionStatusUpdate,
)
from app.services.db.opportunity import addOpportunity
from app.services.db.pipeline_execution_status import (
    create_pipeline_execution_status,
    get_pipeline_execution_status_by_id,
    update_pipeline_execution_status,
)
from app.services.db.pipeline_opportunity_project import (
    create_multiple_pipeline_opportunity_project,
)
from app.services.db.pipeline_opportunity_resource import (
    create_multiple_pipeline_opportunity_resource,
)
from app.services.db.project import get_project_by_ids_list_db
from app.services.db.sales_enablement import add_sales_enablement_db
from app.services.opportunity_status import get_new_opportunity_status_id

logger = logging.getLogger(__name__)


# ============================================================================
# Private Helpers
# ============================================================================

async def _update_execution_status(
    db: AsyncSession,
    execution_status_id: UUID,
    status_update: PipelineExecutionStatusUpdate,
) -> None:
    """Helper to safely update execution status with error logging."""
    try:
        await update_pipeline_execution_status(
            db=db,
            update_data=status_update.model_dump(
                exclude_unset=True,
                exclude_none=True,
            ),
            pipeline_execution_status_id=execution_status_id,
        )
    except Exception:
        logger.exception(
            "Failed to update execution status ID %s", execution_status_id
        )


# ============================================================================
# Pipeline Step Handlers
# ============================================================================

async def handleGetRelaventProjects(
    job_details: dict,
    execution_status_id: UUID,
    client: httpx.AsyncClient,
) -> GetRelaventProjectResponse:
    """Fetches matching projects from AI service and persists them to DB."""
    async with AsyncSessionLocal() as db:
        try:
            execution_status: PipelineExecutionStatusModel = (
                await get_pipeline_execution_status_by_id(
                    db,
                    execution_status_id,
                )
            )
            response = await client.post(
                "/api/v1/projects/match",
                json={"job_details": json.dumps(job_details)},
            )
            response.raise_for_status()

            project_response = GetRelaventProjectResponse(**response.json())

            await create_multiple_pipeline_opportunity_project(
                db=db,
                pipeline_opportunity_projects=[
                    PipelineOpportunityProjectModel(
                        opportunity_id=execution_status.opportunity_id,
                        project_id=row.project_id,
                        project_name=row.project_name,
                        match_score=row.match_score,
                        justification=row.justification,
                        matched_evidence=row.matched_evidence,
                        createdBy=execution_status.createdBy,
                        updatedBy=execution_status.createdBy,
                    )
                    for row in project_response.matches
                ],
            )

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status_id,
                status_update=PipelineExecutionStatusUpdate(
                    projects=PipelineExecutionStatus.COMPLETED,
                    salesEnablement=PipelineExecutionStatus.PENDING,
                    resourceMatch=PipelineExecutionStatus.PENDING,
                    technicalPreperation=PipelineExecutionStatus.PENDING,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text}: "
                        "Updated projects."
                    ),
                ),
            )

            return project_response

        except Exception:
            await db.rollback()
            logger.exception("Failed to fetch Relavent projects")

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status_id,
                status_update=PipelineExecutionStatusUpdate(
                    projects=PipelineExecutionStatus.FAILED,
                    salesEnablement=PipelineExecutionStatus.PENDING,
                    resourceMatch=PipelineExecutionStatus.PENDING,
                    technicalPreperation=PipelineExecutionStatus.PENDING,
                    execution_message=(
                        f"{PipelineExecutionStatus.FAILED.status_text}: "
                        "Could not fetch Relavent projects."
                    ),
                ),
            )
            raise


async def handleSalesEnablement(
    project_id_list: list[int],
    job_details: dict,
    execution_status_id: UUID,
    client: httpx.AsyncClient,
) -> AISalesEnablementResponse:
    """Generates and stores sales enablement assets using AI recommendations."""
    async with AsyncSessionLocal() as db:
        try:
            execution_status: PipelineExecutionStatusModel = (
                await get_pipeline_execution_status_by_id(
                    db,
                    execution_status_id,
                )
            )

            project_details = await get_project_by_ids_list_db(db, project_id_list)

            projects_list = [
                AIProjectRequest(
                    project_name=row.project_name,
                    domain=row.projectDomain.domain,
                    tech_stack=[
                        ts.techstack_name for ts in row.techstacks
                    ] if row.techstacks else [],
                    description=row.description,
                ).model_dump(mode="json")
                for row in project_details
            ]

            response = await client.post(
                "/api/v1/projects/sales-enablement",
                json={
                    "job_details": json.dumps(job_details),
                    "projects": projects_list,
                },
            )
            response.raise_for_status()

            sales_enablement_res = AISalesEnablementResponse(**response.json())

            await add_sales_enablement_db(
                db=db,
                sales_enablement=SalesEnablement(
                    opportunityID=execution_status.opportunity_id,
                    suggested_questions=sales_enablement_res.discovery_questions,
                    sales_talking_points=sales_enablement_res.talking_points,
                    outreach_template=sales_enablement_res.outreach_template,
                    createdBy=execution_status.createdBy,
                    updatedBy=execution_status.createdBy,
                ),
            )

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status_id,
                status_update=PipelineExecutionStatusUpdate(
                    salesEnablement=PipelineExecutionStatus.COMPLETED,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text}: "
                        "Updated Sales Enablement."
                    ),
                ),
            )

            return sales_enablement_res

        except Exception:
            await db.rollback()
            logger.exception("Failed to generate Sales Enablement")

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status_id,
                status_update=PipelineExecutionStatusUpdate(
                    salesEnablement=PipelineExecutionStatus.FAILED,
                    execution_message=(
                        f"{PipelineExecutionStatus.FAILED.status_text}: "
                        "Could not generate Sales Enablement."
                    ),
                ),
            )
            raise


async def handleGetRelaventResource(
    Relavent_resource_request: AIGetRelaventProfilesRequest,
    execution_status_id: UUID,
    client: httpx.AsyncClient,
) -> GetMatchedProfilesResponse:
    """Matches profiles for an opportunity and persists them."""
    async with AsyncSessionLocal() as db:
        try:
            execution_status: PipelineExecutionStatusModel = (
                await get_pipeline_execution_status_by_id(
                    db,
                    execution_status_id,
                )
            )

            response = await client.post(
                "/api/v1/profiles/match",
                json=Relavent_resource_request.model_dump(mode="json"),
            )
            response.raise_for_status()

            matched_profiles_res = GetMatchedProfilesResponse(**response.json())

            await create_multiple_pipeline_opportunity_resource(
                db=db,
                pipeline_opportunity_resources=[
                    PipelineOpportunityResourceModel(
                        opportunity_id=execution_status.opportunity_id,
                        user_id=execution_status.createdBy,
                        email=row.email,
                        variant_id=row.variant_id,
                        variant_title=row.variant_title,
                        experience_years=row.experience_years,
                        match_percentage=row.match_percentage,
                        matching_skills=row.matching_skills,
                        missing_skills=row.missing_skills,
                        justification=row.justification,
                        createdBy=execution_status.createdBy,
                        updatedBy=execution_status.createdBy,
                    )
                    for row in matched_profiles_res.matches
                ],
            )

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status_id,
                status_update=PipelineExecutionStatusUpdate(
                    resourceMatch=PipelineExecutionStatus.COMPLETED,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text}: "
                        "Updated Resources."
                    ),
                ),
            )

            return matched_profiles_res

        except Exception:
            await db.rollback()
            logger.exception("Failed to fetch matching profiles")

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status_id,
                status_update=PipelineExecutionStatusUpdate(
                    resourceMatch=PipelineExecutionStatus.FAILED,
                    execution_message=(
                        f"{PipelineExecutionStatus.FAILED.status_text}: "
                        "Could not fetch Relavent Profiles."
                    ),
                ),
            )
            raise


# ============================================================================
# Pipeline Orchestration
# ============================================================================

async def process_opportunity_pipeline_background(
    job_details: dict,
    execution_status_id: UUID,
) -> None:

    client = get_ai_client()

    project_res = await handleGetRelaventProjects(
        job_details=job_details,
        execution_status_id=execution_status_id,
        client=client,
    )

    top_project_ids = [row.project_id for row in project_res.matches]

    resource_request = AIGetRelaventProfilesRequest(
        job_details=json.dumps(job_details),
        top_project_ids=[str(pid) for pid in top_project_ids],
    )

    await asyncio.gather(
        handleSalesEnablement(
            project_id_list=top_project_ids,
            job_details=job_details,
            execution_status_id=execution_status_id,
            client=client,
        ),
        handleGetRelaventResource(
            Relavent_resource_request=resource_request,
            execution_status_id=execution_status_id,
            client=client,
        ),
    )


async def handleGetScrapedData(
    url: str,
    db: AsyncSession,
    user_id: UUID,
    background_tasks: BackgroundTasks,
) -> CreateOpportunityResponse:
    """Initial entry point: Scrapes URL, saves Opportunity, and queues background pipeline."""
    try:
        client = get_ai_client()
        start_time = perf_counter()

        response = await client.post("/api/v1/scrape", json={"url": url})
        response.raise_for_status()

        ai_response = GetScrapedURLDataResponse(**response.json())
        status_id = await get_new_opportunity_status_id(db)

        opportunity_base = OpportunityBase(
            **ai_response.job_details,
            company_profile=ai_response.company_profile,
            job_posting_url=url,
            is_ai_scraped=True,
            status_id=status_id,
            platform=ai_response.platform,
            createdBy=user_id,
            updatedBy=user_id,
        )

        opportunity = await addOpportunity(
            Opportunity(**opportunity_base.model_dump()),
            db,
        )

        execution_status = await create_pipeline_execution_status(
            db=db,
            pipeline_execution_status=PipelineExecutionStatusModel(
                execution_message=PipelineExecutionStatus.PENDING.status_text,
                opportunity_id=opportunity.opportunityID,
                createdBy=user_id,
                updatedBy=user_id,
            ),
        )

        background_tasks.add_task(
            process_opportunity_pipeline_background,
            ai_response.job_details,
            execution_status.id,
        )

        logger.info(
            "Scrape execution completed in %.2f seconds",
            perf_counter() - start_time,
        )

        return CreateOpportunityResponse(
            message="Opportunity fetched from AI successfully",
            opportunityID=opportunity.opportunityID,
        )

    except Exception as exc:
        logger.exception("Failed to process scraped data for URL %s", url)
        raise handle_ai_exception(exc) from exc




async def handleGetManualScrapedData(
    AIManualJDRequest: AIManualJDRequest,
    db: AsyncSession,
    user_id: UUID,
    background_tasks: BackgroundTasks,
) -> CreateOpportunityResponse:
    """Initial entry point: Scrapes URL, saves Opportunity, and queues background pipeline."""
    try:
        client = get_ai_client()
        start_time = perf_counter()

        response = await client.post("/api/v1/manual-entry", json=AIManualJDRequest.model_dump(mode="json"))
        response.raise_for_status()

        ai_response = GetScrapedURLDataResponse(**response.json())
        status_id = await get_new_opportunity_status_id(db)

        opportunity_base = OpportunityBase(
            **ai_response.job_details,
            company_profile=ai_response.company_profile,
            job_posting_url=AIManualJDRequest.company_website,
            is_ai_scraped=False,
            status_id=status_id,
            platform=ai_response.platform,
            createdBy=user_id,
            updatedBy=user_id,
        )

        opportunity = await addOpportunity(
            Opportunity(**opportunity_base.model_dump()),
            db,
        )

        execution_status = await create_pipeline_execution_status(
            db=db,
            pipeline_execution_status=PipelineExecutionStatusModel(
                execution_message=PipelineExecutionStatus.PENDING.status_text,
                opportunity_id=opportunity.opportunityID,
                createdBy=user_id,
                updatedBy=user_id,
            ),
        )

        background_tasks.add_task(
            process_opportunity_pipeline_background,
            ai_response.job_details,
            execution_status.id,
        )

        logger.info(
            "Scrape execution completed in %.2f seconds",
            perf_counter() - start_time,
        )

        return CreateOpportunityResponse(
            message="Opportunity fetched from AI successfully",
            opportunityID=opportunity.opportunityID,
        )

    except Exception as exc:
        logger.exception("Failed to process scraped data for URL %s", AIManualJDRequest.company_website)
        raise handle_ai_exception(exc) from exc