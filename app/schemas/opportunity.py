from datetime import datetime

from pydantic import BaseModel,Field,ConfigDict

class CompanyProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    overview: str | None = None
    industry: str | None = None
    products_services: str | None = None
    headquarters: str | None = None
    location: str | None = None


class OpportunityBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    industry: str | None = None
    role: str | None = None
    experience: str | None = None
    duration: str | None = None
    level: str | None = None
    salary: str | None = None
    posted_date: str | None = None
    required_skills: list[str] | None = []
    preferred_skills: list[str] | None = []
    description: str | None = None
    responsibilities: list[str] | None = []
    requirements: list[str] | None = []
    benefits: list[str] | None = []
    client_information: str | None = None
    apply_url: str | None = None
    ai_job_summary: str | None = None
    required_proposal_questions: list[str] | None = []
    company_profile: CompanyProfileBase | None = None
    additional_fields: dict | None = None


class OpportunityCreate(OpportunityBase):
    pass

class GetOpportunityContent(BaseModel):
    url : str = Field(...,description="URL that must be scraped")

    
class OpportunityRead(OpportunityBase):
    opportunityID: int
    createdBy: int
    updatedBy: int
    createdAt: datetime
    updatedAt: datetime | None = None

    model_config = {"from_attributes": True}
