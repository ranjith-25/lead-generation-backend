from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.opportunity_status import OpportunityStatusDTO, OpportunityStatusListRead


class GetOpportunityStatusResponse(BaseResponse):
    opportunityStatus: Optional[OpportunityStatusDTO] = Field(None, description="Opportunity Status")
    opportunityStatusList: Optional[list[OpportunityStatusListRead]] = Field(None, description="Opportunity Status List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreateOpportunityStatusResponse(BaseResponse):
    newOpportunityStatus: OpportunityStatusDTO = Field(..., description="New Opportunity Status Created")
    status_code: int = Field(200)


class UpdateOpportunityStatusResponse(BaseResponse):
    updatedOpportunityStatus: OpportunityStatusDTO = Field(..., description="Opportunity Status Updated")
    status_code: int = Field(200)


class DeleteOpportunityStatusResponse(BaseResponse):
    status_code: int = Field(200)
