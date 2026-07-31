from app.responses.base import BaseResponse
from app.schemas.opportunity import OpportunityBase, CompanyProfileBase

class GetOpportunityResponse(BaseResponse):
    job_details : OpportunityBase | None = None
    company_profile : CompanyProfileBase | None = None
