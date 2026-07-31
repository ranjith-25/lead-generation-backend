from app.exceptions.ai_exception import handle_ai_exception
import httpx
from httpx import AsyncClient
from app.core.connections.ai_connection import get_ai_client
import logging
from app.services.db.opportunity import addOpportunity
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityBase
from app.responses.opportunity import GetOpportunityResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.responses.ai import GetScrapedURLDataResponse


async def handleGetScrapedData(url: str, db: AsyncSession):
    try:
        client = get_ai_client()

        body = {"url": url}

        response = await client.post(
            "/api/v1/scrape",
            json=body,
        )

        response.raise_for_status()

        aiResponse = GetScrapedURLDataResponse(**response.json())

        opportunityBase = OpportunityBase(**aiResponse.job_details)

        opportunity = Opportunity( **opportunityBase.model_dump() )

        result: Opportunity = await addOpportunity(opportunity, db)

        return GetOpportunityResponse(
            message="Opportunity fetched from AI successfully",
            opportunityDetails=OpportunityBase.model_validate(result),
        )

    except Exception as exc:
        logging.exception("Could not get scraped data")
        raise handle_ai_exception(exc) from exc
