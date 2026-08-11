from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, AliasChoices

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
    description: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    industry: str | None = None
    role: str | None = None
    experience: str | None = None
    duration: str | None = None
    level: str | None = None
    salary: str | None = None
    posted_date: str | None = Field(None, validation_alias=AliasChoices("posted_at", "posted_date"))
    required_skills: list[str] | None = []
    preferred_skills: list[str] | None = []
    benefits: list[str] | None = []
    client_information: dict | None = None
    apply_url: str | None = None
    ai_job_summary: str | None = None
    required_proposal_questions: list[str] | None = []
    company_profile: CompanyProfileBase | None = None
    job_posting_url: str | None = None
    company_website: str | None = None
    additional_notes: str | None = None
    is_ai_scraped: bool = True
    platform: str | None = None
    status_id: UUID
    additional_fields: dict | None = None
    createdBy: UUID | None = None
    updatedBy: UUID | None = None
    assigned_to: UUID | None = None


class OpportunityCreate(BaseModel):
    title: str
    company: str
    company_website: str | None = None
    experience: str | None = None
    description: str
    additional_notes: str | None = None

class OpportunityStatusUpdate(BaseModel):
    status_id: UUID

class GetOpportunityContent(BaseModel):
    url : str = Field(...,description="URL that must be scraped")

    
class OpportunityFilterRequest(BaseModel):
    search: str | None = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    view: str | None = "My view"
    status: list[str] | None = None
    platform: list[str] | None = None
    company: list[str] | None = None
    role: list[str] | None = None
    location: list[str] | None = None
    team: list[str] | None = None

class TeamMemberFilter(BaseModel):
    user_id: UUID
    fullName: str

class OpportunityFilterValuesResponse(BaseModel):
    status: list[str]
    platform: list[str]
    company: list[str]
    role: list[str]
    location: list[str]
    team: list[TeamMemberFilter] | None = None

class OpportunityStatusRead(BaseModel):
    id: UUID
    status: str
    description: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class OpportunityRead(OpportunityBase):
    opportunityID: UUID
    createdBy: str = Field(validation_alias=AliasChoices("createdByName", "createdBy"))
    updatedBy: str = Field(validation_alias=AliasChoices("updatedByName", "updatedBy"))
    assignedToName: str | None = Field(default=None, validation_alias=AliasChoices("assignedToName", "assigned_to"))
    createdAt: datetime
    updatedAt: datetime | None = None
    status: str | None = Field(default=None, validation_alias=AliasChoices("statusName", "status"))


class OpportunityListRead(BaseModel):
    opportunityID: UUID
    title: str
    company: str | None = None
    client_information: dict | None = None
    platform: str | None = None
    createdBy: str = Field(validation_alias=AliasChoices("createdByName", "createdBy"))
    updatedBy: str = Field(validation_alias=AliasChoices("updatedByName", "updatedBy"))
    assignedToName: str | None = Field(default=None, validation_alias=AliasChoices("assignedToName", "assigned_to"))
    createdAt: datetime
    updatedAt: datetime | None = None
    status: str | None = Field(default=None, validation_alias=AliasChoices("statusName", "status"))

    model_config = ConfigDict(from_attributes=True)


class OpportunityPaginatedResponse(BaseModel):
    data: list[OpportunityListRead]
    total: int
    page: int
    size: int
    total_pages: int
