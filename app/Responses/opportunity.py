from app.responses.base import BaseResponse
from app.schemas.opportunity import OpportunityBase

class GetOpportunityResponse(BaseResponse):
    opportunityDetails : OpportunityBase | None = None
