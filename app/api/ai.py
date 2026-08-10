from fastapi.routing import APIRouter
from fastapi import Depends

from app.services.ai import handleGetScrapedData
from app.responses.opportunity import CreateOpportunityResponse
from app.schemas.opportunity import GetOpportunityContent
from app.api.deps import get_current_user
from app.core.connections.postgres import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_permission
from fastapi import BackgroundTasks
router = APIRouter(prefix="/ai",tags=["AI"])

@router.post("")
async def get_scrapped_data(request : GetOpportunityContent,backgroundTasks : BackgroundTasks,current_user : User = Depends(require_permission("ai_discovery","create")),db: AsyncSession = Depends(get_db)):
    response : CreateOpportunityResponse = await handleGetScrapedData(request.url,db, current_user.user_id,backgroundTasks=backgroundTasks)
    return response