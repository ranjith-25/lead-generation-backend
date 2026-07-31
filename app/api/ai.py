from fastapi.routing import APIRouter
from fastapi import Depends

from app.services.ai import handleGetScrapedData
from app.responses.opportunity import GetOpportunityResponse
from app.schemas.opportunity import GetOpportunityContent
from app.api.deps import get_current_user
from app.core.connections.postgres import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ai",tags=["AI"])

@router.post("")
async def get_scrapped_data(request : GetOpportunityContent,current_user : User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    response : GetOpportunityResponse = await handleGetScrapedData(request.url,db)
    return response