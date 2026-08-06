from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.opportunity_status import OpportunityStatusDTO


class GetOpportunityStatusResponse(BaseResponse):
    opportunityStatus: Optional[OpportunityStatusDTO] = Field(None, description="Opportunity Status")
    opportunityStatusList: Optional[list[OpportunityStatusDTO]] = Field(None, description="Opportunity Status List")
    status_code: int = Field(200)


class CreateOpportunityStatusResponse(BaseResponse):
    newOpportunityStatus: OpportunityStatusDTO = Field(..., description="New Opportunity Status Created")
    status_code: int = Field(200)


class UpdateOpportunityStatusResponse(BaseResponse):
    updatedOpportunityStatus: OpportunityStatusDTO = Field(..., description="Opportunity Status Updated")
    status_code: int = Field(200)


class DeleteOpportunityStatusResponse(BaseResponse):
    status_code: int = Field(200)
