from app.exceptions.ai_exception import handle_ai_exception
from app.core.connections.ai_connection import get_ai_client
import logging
from app.services.db.opportunity import addOpportunity
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityBase
from app.responses.opportunity import CreateOpportunityResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.responses.ai import GetScrapedURLDataResponse,GetRelaventProjectResponse, AIProjectResponse
import httpx
from fastapi import BackgroundTasks
import json
from time import perf_counter
import asyncio
from app.services.db.project import get_project_by_ids_list_db
from app.schemas.project import AIProjectRequest

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
        "/api/v1/sales-enablement",
        json=body,
        )
        print("Response from AI Sales Enablement points : ", response.json())

        projectResponse : GetRelaventProjectResponse = GetRelaventProjectResponse(**response.json())


        response.raise_for_status()

        return projectResponse
    

    
    except Exception as exc:
        logging.exception("Could not get Projects for corresponding Opportunity")
        return

async def handleGetRelaventProjects(jobDetails : dict,client : httpx.AsyncClient ,db: AsyncSession):
    try:

        body : dict = {
        "job_details" : json.dumps(jobDetails)
       }

        response = await client.post(
        "/api/v1/projects/match",
        json=body,
       )
        print("Response from AI", response.json())

        projectResponse : GetRelaventProjectResponse = GetRelaventProjectResponse(**response.json())
       
        await handleSalesEnablement([match.project_id for match in projectResponse.matches],jobDetails,client,db)

        response.raise_for_status()

        return projectResponse
       

       
    except Exception as exc:
        logging.exception("Could not get Projects for corresponding Opportunity")
        return


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

        backgroundTasks.add_task(
            handleGetRelaventProjects ,
            aiResponse.job_details,
            client,
            db
        )


        opportunityBase = OpportunityBase(
            **aiResponse.job_details,
            company_profile=aiResponse.company_profile,
            job_posting_url=url,
            is_ai_scraped=True,
            platform=aiResponse.platform,
            createdBy=user_id,
            updatedBy=user_id
        )

        opportunity = Opportunity( **opportunityBase.model_dump() )

        # result: Opportunity = await addOpportunity(opportunity, db)

        endpref = perf_counter()
        print(f" Time required Scrape ai execution : {endpref-startpref}")

        return CreateOpportunityResponse(
            message="Opportunity fetched from AI successfully",
            opportunityID=16
        )

    except Exception as exc:
        logging.exception("Could not get scraped data")
        raise handle_ai_exception(exc) from exc
