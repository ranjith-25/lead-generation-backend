from app.responses.base import BaseResponse
from app.schemas.opportunity import OpportunityBase, CompanyProfileBase
from uuid import UUID

class GetOpportunityResponse(BaseResponse):
    job_details : OpportunityBase | None = None
    company_profile : CompanyProfileBase | None = None

class CreateOpportunityResponse(BaseResponse):
    opportunityID: UUID

