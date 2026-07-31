from fastapi.routing import APIRouter
from app.services.ai import handleGetScrapedData
from app.responses.opportunity import GetOpportunityResponse
from app.schemas.opportunity import GetOpportunityContent
from app.api.deps import get_current_user
from app.core.connections.postgres import get_db
from fastapi import Depends
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

aiRouter = APIRouter(prefix="/ai",tags=["AI"])

@aiRouter.post("/")
async def getScrappedData(request : GetOpportunityContent,current_user : User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    response : GetOpportunityResponse = await handleGetScrapedData(request.url,db)
    return response