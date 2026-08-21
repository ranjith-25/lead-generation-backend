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
from app.exceptions.custom import AppException, OpportunityAlreadyExistsException
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
    GetTechnicalPreperationResponse
)
from app.responses.opportunity import CreateOpportunityResponse
from app.schemas.ai import AIGetRelaventProfilesRequest, AIGetRelevantProjectsRequest , AIManualJDRequest, AISalesEnablementRequest ,AITechnicalPreperationRequest, AIURLScrapeRequest
from app.schemas.notification import NotificationType
from app.schemas.opportunity import OpportunityBase
from app.schemas.project import AIProjectRequest
from app.schemas.pipeline_execution_status import (
    PipelineExecutionStatus,
    PipelineExecutionStatusUpdate,
)
from app.services.db.opportunity import addOpportunity, get_opportunity_by_url
from app.services.db.pipeline_execution_status import (
    create_pipeline_execution_status,
    get_pipeline_execution_status_by_id,
    update_pipeline_execution_status,
    get_pipeline_execution_status_by_opportunity_id
)
from app.services.db.pipeline_opportunity_project import (
    create_multiple_pipeline_opportunity_project,
)
from app.services.db.job_role import create_job_role
from app.services.db.pipeline_opportunity_resource import (
    create_multiple_pipeline_opportunity_resource,
)
from app.models.job_role import JobRole
from app.services.db.project import get_project_by_ids_list_db
from app.services.db.sales_enablement import add_sales_enablement_db
from app.services.notification_dispatcher import notify_users
from app.services.opportunity_status import get_new_opportunity_status_id
from app.config import LogAction
from app.services.system_log import log_activity

from app.services.db.pipeline_opportunity_techincal_preperation import create_multiple_pipeline_opportunity_technical_preperation
from app.models.pipeline_opportunity_techincal_preperation import PipelineOpportunityTechnicalPreperationModel
from app.services.db.job_role import get_all_job_roles
from app.schemas.job_role import JobRoleFilters
from app.config import JOBKEY_QUERY_URL

logger = logging.getLogger(__name__)

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
            request = AIGetRelevantProjectsRequest(
                user_id=execution_status.createdBy,
                action="Get Relevant Projects",
                job_details=json.dumps(job_details)
            )
            response = await client.post(
                "/api/v1/projects/match",
                json=request.model_dump(mode="json"),
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
            return


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
            request = AISalesEnablementRequest(
                user_id=execution_status.createdBy,
                action="Generate Sales Enablement",
                job_details= json.dumps(job_details),
                projects=projects_list
            )


            response = await client.post(
                "/api/v1/projects/sales-enablement",
                json=request.model_dump(mode="json")
            )

            if response.status_code != 200:
                logger.exception(f"Sales Enablement failed: {response.text} \n Payload {request.model_dump()}")
                raise Exception("Sales Enablement failed")
                
            response.raise_for_status()
            sales_enablement_res = AISalesEnablementResponse(**response.json())

            await add_sale s_enablement_db(
                db=db,
                sales_enablement=SalesEnablement(
                    opportunityID=execution_status.opportunity_id,
                    suggested_questions=sales_enablement_res.discovery_questions,
                    sales_talking_points=sales_enablement_res.talking_points,
                    outreach_template=sales_enablement_res.outreach_template,
                    outreach_subject=sales_enablement_res.outreach_subject,
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
                        user_id=row.candidate_id,
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



async def handleTechnicalPreperation(
    technical_preperation_request: AITechnicalPreperationRequest,
    opportunity_id: UUID
) -> GetTechnicalPreperationResponse:
    """Matches profiles for an opportunity and persists them."""
    async with AsyncSessionLocal() as db:

        execution_status: PipelineExecutionStatusModel = (
                await get_pipeline_execution_status_by_opportunity_id(
                    db,
                    opportunity_id,
                )
            )
        try:
            
            client = get_ai_client()
            response = await client.post(
                "/api/v1/preparations/technical",
                json=technical_preperation_request.model_dump(mode="json"),
            )
            response.raise_for_status()

            technical_preperation_res = GetTechnicalPreperationResponse(**response.json())

            await create_multiple_pipeline_opportunity_technical_preperation(
                db=db,
                pipeline_opportunity_technical_preperations=[
                    PipelineOpportunityTechnicalPreperationModel(
                        opportunity_id=execution_status.opportunity_id,
                        candidate_name=technical_preperation_res.candidate_name,
                        variant_title=technical_preperation_res.variant_title,
                        technical_briefing_note=technical_preperation_res.technical_briefing_note,
                        interview_preparation_guide= [row.model_dump(mode="json") for row in technical_preperation_res.interview_preparation_guide],
                        createdBy=execution_status.createdBy,   
                        updatedBy=execution_status.createdBy,
                    )
                ],
            )

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status.id,
                status_update=PipelineExecutionStatusUpdate(
                    technicalPreperation=PipelineExecutionStatus.COMPLETED,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text}: "
                        "Updated Technical Preperation."
                    ),
                ),
            )

            return technical_preperation_res

        except Exception:
            await db.rollback()
            logger.exception("Failed to fetch Technical Preperation")

            await _update_execution_status(
                db=db,
                execution_status_id=execution_status.id,
                status_update=PipelineExecutionStatusUpdate(
                    technicalPreperation=PipelineExecutionStatus.FAILED,
                    execution_message=(
                        f"{PipelineExecutionStatus.FAILED.status_text}: "
                        "Could not fetch Technical Preperation."
                    ),
                ),
            )
            return

# ============================================================================
# Pipeline Orchestration
# ============================================================================

async def process_opportunity_pipeline_background(
    job_details: dict,
    execution_status_id: UUID,
    user_id: UUID
) -> None:

    client = get_ai_client()

    project_res = await handleGetRelaventProjects(
        job_details=job_details,
        execution_status_id=execution_status_id,
        client=client,
    )
    
    if project_res is None:
        raise 
    
    top_project_ids = [row.project_id for row in project_res.matches]

    resource_request = AIGetRelaventProfilesRequest(
        user_id=user_id,
        action="Get Relevant Profiles ",
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
        can_continue = True
        for jobkey_url in JOBKEY_QUERY_URL:
            if jobkey_url in url:
                can_continue: False
                
        if can_continue:
            url = url.split('?')[0]
            
        existing_opportunity = await get_opportunity_by_url(db, url)
        if existing_opportunity:
            raise OpportunityAlreadyExistsException(existing_opportunity.opportunityID)

        client = get_ai_client()
        start_time = perf_counter()
        
        all_job_roles = [job_role.roleName for job_role in (await get_all_job_roles(db, JobRoleFilters()))]
        request = AIURLScrapeRequest(user_id=user_id,action="Overview & Analysis",url=url,job_roles=all_job_roles,)
        response = await client.post("/api/v1/scrape", json=request.model_dump(mode="json"))
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

        # Staged before the next commit (create_pipeline_execution_status) flushes it.
        await log_activity(
            db,
            LogAction.OPPORTUNITY_AI_INGESTED,
            user_id,
            entity_type="opportunity",
            entity_id=opportunity.opportunityID,
            entity_name=opportunity.title,
            details={
                "job_posting_url": url,
                "platform": opportunity.platform,
                "company": opportunity.company,
            },
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
            user_id
        )

        logger.info(
            "Scrape execution completed in %.2f seconds",
            perf_counter() - start_time,
        )

        if opportunity.role not in all_job_roles:
            await create_job_role(db, JobRole(
                roleName= opportunity.role,
                createdBy= user_id,
                updatedBy= user_id
            ))
        await notify_users(
            db,
            user_ids=[user_id],
            notification_type=NotificationType.ANALYSIS_COMPLETE,
            context={"opportunity_id": str(opportunity.opportunityID)},
            created_by=user_id,
        )

        return CreateOpportunityResponse(
            message="Opportunity fetched from AI successfully",
            opportunityID=opportunity.opportunityID,
        )

    except AppException:
        raise

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

        # Manual create path (create_opportunity_service); staged before the next commit
        # (create_pipeline_execution_status) flushes it.
        await log_activity(
            db,
            LogAction.OPPORTUNITY_CREATED,
            user_id,
            entity_type="opportunity",
            entity_id=opportunity.opportunityID,
            entity_name=opportunity.title,
            details={
                "company": opportunity.company,
                "role": opportunity.role,
                "source": "manual",
            },
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
            user_id
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