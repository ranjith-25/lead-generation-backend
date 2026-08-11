from app.api.pipeline_execution_status import get_pipeline_execution_status_by_id
from app.exceptions.ai_exception import handle_ai_exception
from app.core.connections.ai_connection import get_ai_client
import logging
from app.services.db.opportunity import addOpportunity
from app.models.opportunity import Opportunity
from app.models.sales_enablement import SalesEnablement
from app.models.sales_enablement import SalesEnablement
from app.schemas.opportunity import OpportunityBase
from app.responses.opportunity import CreateOpportunityResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.responses.ai import GetScrapedURLDataResponse,GetRelaventProjectResponse, AIProjectResponse , AISalesEnablementResponse
from app.responses.ai import GetScrapedURLDataResponse,GetRelaventProjectResponse, AIProjectResponse , AISalesEnablementResponse
import httpx
from fastapi import BackgroundTasks
import json
from time import perf_counter
import asyncio
from app.services.db.project import get_project_by_ids_list_db
from app.schemas.project import AIProjectRequest
from app.models.pipeline_execution_status import PipelineExecutionStatusModel
from app.models.pipeline_opportunity_project import PipelineOpportunityProjectModel
from app.schemas.pipeline_execution_status import PipelineExecutionStatus,PipelineExecutionStatusCreate,PipelineExecutionStatusUpdate
from app.services.db.pipeline_execution_status import get_pipeline_execution_status_by_id
from app.services.db.pipeline_execution_status import get_pipeline_execution_status_by_id

from app.services.db.pipeline_execution_status import create_pipeline_execution_status,update_pipeline_execution_status
from app.services.db.sales_enablement import add_sales_enablement_db
from app.services.db.sales_enablement import add_sales_enablement_db

from app.services.db.pipeline_opportunity_project import create_multiple_pipeline_opportunity_project

from app.core.connections.postgres import get_db ,AsyncSessionLocal
from app.core.connections.postgres import get_db ,AsyncSessionLocal
from app.core.connections.ai_connection import get_ai_client


from uuid import UUID

from app.services.opportunity_status import get_new_opportunity_status_id
async def handleSalesEnablement(project_id_list : list[int],jobDetails: dict,client : httpx.AsyncClient,db: AsyncSession):
    try:
        projectDetails = await get_project_by_ids_list_db(db,project_id_list)
        projectsList = [
            AIProjectRequest(
                project_name=row.project_name,
                domain=row.projectDomain.domain,
                tech_stack= [techstack.techstack_name for techstack in row.techstacks] if row.techstacks else [],
                description=row.description
            ) for row in projectDetails
        ]
        body : dict = {
        "job_details" : json.dumps(jobDetails),
        "projects" : projectsList,
        }

            response = await client.post(
            "/api/v1/projects/sales-enablement",
            json=body,
            )
            response.raise_for_status()
            print("Response from AI Sales Enablement points : ", response.json())
            response = await client.post(
            "/api/v1/projects/sales-enablement",
            json=body,
            )
            response.raise_for_status()
            print("Response from AI Sales Enablement points : ", response.json())

            salesEnablementResponse : AISalesEnablementResponse = AISalesEnablementResponse(
                **response.json()
            )

            executionStatus : PipelineExecutionStatusModel = await get_pipeline_execution_status_by_id(
                db,
                executionStatusID
            )

            await add_sales_enablement_db(
                db = db,
                sales_enablement= SalesEnablement(
                    opportunityID = executionStatus.opportunity_id,
                    suggested_questions = salesEnablementResponse.discovery_questions,
                    sales_talking_points = salesEnablementResponse.talking_points,
                    outreach_template = salesEnablementResponse.outreach_template,
                    createdBy = executionStatus.createdBy,
                    updatedBy = executionStatus.createdBy
                )

            )

            
            await update_pipeline_execution_status(
                db=db,
                update_data=PipelineExecutionStatusUpdate(
                    salesEnablement=PipelineExecutionStatus.COMPLETED,
                    resourceMatch=PipelineExecutionStatus.PENDING,
                    technicalPreperation=PipelineExecutionStatus.PENDING,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text} "
                        ": Updated Sales Enablement."
                    )
                ).model_dump(
                    exclude_unset=True,
                    exclude_none=True
                ),
                pipeline_execution_status_id=executionStatusID
            )


            return salesEnablementResponse
            salesEnablementResponse : AISalesEnablementResponse = AISalesEnablementResponse(
                **response.json()
            )

            executionStatus : PipelineExecutionStatusModel = await get_pipeline_execution_status_by_id(
                db,
                executionStatusID
            )

            await add_sales_enablement_db(
                db = db,
                sales_enablement= SalesEnablement(
                    opportunityID = executionStatus.opportunity_id,
                    suggested_questions = salesEnablementResponse.discovery_questions,
                    sales_talking_points = salesEnablementResponse.talking_points,
                    outreach_template = salesEnablementResponse.outreach_template,
                    createdBy = executionStatus.createdBy,
                    updatedBy = executionStatus.createdBy
                )

            )

            
            await update_pipeline_execution_status(
                db=db,
                update_data=PipelineExecutionStatusUpdate(
                    salesEnablement=PipelineExecutionStatus.COMPLETED,
                    resourceMatch=PipelineExecutionStatus.PENDING,
                    technicalPreperation=PipelineExecutionStatus.PENDING,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text} "
                        ": Updated Sales Enablement."
                    )
                ).model_dump(
                    exclude_unset=True,
                    exclude_none=True
                ),
                pipeline_execution_status_id=executionStatusID
            )


        return salesEnablementResponse
    

    
        except Exception as exc:
            try:
                await update_pipeline_execution_status(
                    db=db,
                    update_data=PipelineExecutionStatusUpdate(
                        projects=PipelineExecutionStatus.FAILED,
                        salesEnablement=PipelineExecutionStatus.PENDING,
                        resourceMatch=PipelineExecutionStatus.PENDING,
                        technicalPreperation=PipelineExecutionStatus.PENDING,
                        execution_message=(
                            f"{PipelineExecutionStatus.FAILED.status_text} "
                            ": Could not fetch relevant projects."
                        )
                    ).model_dump(
                        exclude_unset=True,
                        exclude_none=True
                    ),
                    pipeline_execution_status_id=executionStatusID
                )

            except Exception:
                logging.exception(
                    "Could not update project execution status"
                )
        raise
    
async def handleGetRelaventProjects(
    jobDetails: dict,
    executionStatusID: UUID
):
    async with AsyncSessionLocal() as db:
        try:
            client = get_ai_client()
        except Exception as exc:
            try:
                await update_pipeline_execution_status(
                    db=db,
                    update_data=PipelineExecutionStatusUpdate(
                        projects=PipelineExecutionStatus.FAILED,
                        salesEnablement=PipelineExecutionStatus.PENDING,
                        resourceMatch=PipelineExecutionStatus.PENDING,
                        technicalPreperation=PipelineExecutionStatus.PENDING,
                        execution_message=(
                            f"{PipelineExecutionStatus.FAILED.status_text} "
                            ": Could not fetch relevant projects."
                        )
                    ).model_dump(
                        exclude_unset=True,
                        exclude_none=True
                    ),
                    pipeline_execution_status_id=executionStatusID
                )

            except Exception:
                logging.exception(
                    "Could not update project execution status"
                )
        raise
    
async def handleGetRelaventProjects(
    jobDetails: dict,
    executionStatusID: UUID
):
    async with AsyncSessionLocal() as db:
        try:
            client = get_ai_client()

            executionStatus : PipelineExecutionStatusModel  = await get_pipeline_execution_status_by_id(
                db,
                executionStatusID
            )

            body = {
                "job_details": json.dumps(jobDetails)
            }

            response = await client.post(
                "/api/v1/projects/match",
                json=body
            )

            # Do this immediately after the AI call
            response.raise_for_status()

            print("Response from AI", response.json())
            response = await client.post(
                "/api/v1/projects/match",
                json=body
            )

            # Do this immediately after the AI call
            response.raise_for_status()

            print("Response from AI", response.json())

            projectResponse = GetRelaventProjectResponse(
                **response.json()
            )
            projectResponse = GetRelaventProjectResponse(
                **response.json()
            )

            await create_multiple_pipeline_opportunity_project(
                db=db,
                pipeline_opportunity_projects=[
                    PipelineOpportunityProjectModel(
                        opportunity_id=executionStatus.opportunity_id,
                        project_id=row.project_id,
                        project_name=row.project_name,
                        match_score=row.match_score,
                        justification=row.justification,
                        matched_evidence=row.matched_evidence,
                        createdBy=executionStatus.createdBy,
                        updatedBy=executionStatus.createdBy
                    )
                    for row in projectResponse.matches
                ]
            )
            await create_multiple_pipeline_opportunity_project(
                db=db,
                pipeline_opportunity_projects=[
                    PipelineOpportunityProjectModel(
                        opportunity_id=executionStatus.opportunity_id,
                        project_id=row.project_id,
                        project_name=row.project_name,
                        match_score=row.match_score,
                        justification=row.justification,
                        matched_evidence=row.matched_evidence,
                        createdBy=executionStatus.createdBy,
                        updatedBy=executionStatus.createdBy
                    )
                    for row in projectResponse.matches
                ]
            )

            await update_pipeline_execution_status(
                db=db,
                update_data=PipelineExecutionStatusUpdate(
                    projects=PipelineExecutionStatus.COMPLETED,
                    salesEnablement=PipelineExecutionStatus.PENDING,
                    resourceMatch=PipelineExecutionStatus.PENDING,
                    technicalPreperation=PipelineExecutionStatus.PENDING,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text} "
                        ": Updated projects."
                    )
                ).model_dump(
                    exclude_unset=True,
                    exclude_none=True
                ),
                pipeline_execution_status_id=executionStatusID
            )

            await handleSalesEnablement(
                project_id_list=[row.project_id for row in projectResponse.matches],
                jobDetails=jobDetails,
                executionStatusID=executionStatusID
            )
            await update_pipeline_execution_status(
                db=db,
                update_data=PipelineExecutionStatusUpdate(
                    projects=PipelineExecutionStatus.COMPLETED,
                    salesEnablement=PipelineExecutionStatus.PENDING,
                    resourceMatch=PipelineExecutionStatus.PENDING,
                    technicalPreperation=PipelineExecutionStatus.PENDING,
                    execution_message=(
                        f"{PipelineExecutionStatus.COMPLETED.status_text} "
                        ": Updated projects."
                    )
                ).model_dump(
                    exclude_unset=True,
                    exclude_none=True
                ),
                pipeline_execution_status_id=executionStatusID
            )

            await handleSalesEnablement(
                project_id_list=[row.project_id for row in projectResponse.matches],
                jobDetails=jobDetails,
                executionStatusID=executionStatusID
            )

            return projectResponse
            return projectResponse

        except Exception:
            await db.rollback()

            logging.exception(
                "Could not get Projects for corresponding Opportunity"
            )

            try:
                await update_pipeline_execution_status(
                    db=db,
                    update_data=PipelineExecutionStatusUpdate(
                        projects=PipelineExecutionStatus.FAILED,
                        salesEnablement=PipelineExecutionStatus.PENDING,
                        resourceMatch=PipelineExecutionStatus.PENDING,
                        technicalPreperation=PipelineExecutionStatus.PENDING,
                        execution_message=(
                            f"{PipelineExecutionStatus.FAILED.status_text} "
                            ": Could not fetch relevant projects."
                        )
                    ).model_dump(
                        exclude_unset=True,
                        exclude_none=True
                    ),
                    pipeline_execution_status_id=executionStatusID
                )

            except Exception:
                logging.exception(
                    "Could not update project execution status"
                )

            raise
        except Exception:
            await db.rollback()

            logging.exception(
                "Could not get Projects for corresponding Opportunity"
            )

            try:
                await update_pipeline_execution_status(
                    db=db,
                    update_data=PipelineExecutionStatusUpdate(
                        projects=PipelineExecutionStatus.FAILED,
                        salesEnablement=PipelineExecutionStatus.PENDING,
                        resourceMatch=PipelineExecutionStatus.PENDING,
                        technicalPreperation=PipelineExecutionStatus.PENDING,
                        execution_message=(
                            f"{PipelineExecutionStatus.FAILED.status_text} "
                            ": Could not fetch relevant projects."
                        )
                    ).model_dump(
                        exclude_unset=True,
                        exclude_none=True
                    ),
                    pipeline_execution_status_id=executionStatusID
                )

            except Exception:
                logging.exception(
                    "Could not update project execution status"
                )

            raise

async def handleGetScrapedData(url: str, db: AsyncSession, user_id , backgroundTasks : BackgroundTasks) -> CreateOpportunityResponse:
    try:
        client = get_ai_client()
        startpref = perf_counter()

        body = {"url": url}

        response = await client.post(
            "/api/v1/scrape",
            json=body,
        )

        response.raise_for_status()

        aiResponse = GetScrapedURLDataResponse(**response.json())

        status_id = await get_new_opportunity_status_id(db)
        status_id = await get_new_opportunity_status_id(db)


        opportunityBase = OpportunityBase(
            **aiResponse.job_details,
            company_profile=aiResponse.company_profile,
            job_posting_url=url,
            is_ai_scraped=True,
            status_id=status_id,
            status_id=status_id,
            platform=aiResponse.platform,
            createdBy=user_id,
            updatedBy=user_id
        )

        opportunity = Opportunity( **opportunityBase.model_dump() )

        result: Opportunity = await addOpportunity(opportunity, db)

        result_pipeline_executionStatus : PipelineExecutionStatus = await create_pipeline_execution_status(
        result_pipeline_executionStatus : PipelineExecutionStatus = await create_pipeline_execution_status(
            db=db,
            pipeline_execution_status=PipelineExecutionStatusModel(
                execution_message = PipelineExecutionStatus.PENDING.status_text,
                opportunity_id = result.opportunityID,
                createdBy = user_id,
                updatedBy = user_id
            )
        )
        backgroundTasks.add_task(
            handleGetRelaventProjects ,
            aiResponse.job_details,
            result_pipeline_executionStatus.id
        )

        endpref = perf_counter()
        print(f" Time required Scrape ai execution : {endpref-startpref}")

        return CreateOpportunityResponse(
            message="Opportunity fetched from AI successfully",
            opportunityID=result.opportunityID
        )

    except Exception as exc:
        logging.exception("Could not get scraped data")
        raise handle_ai_exception(exc) from exc
