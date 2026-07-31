from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OpportunityBase(BaseModel):
    status: str | None = None
    title: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    experience: str | None = None
    salary: str | None = None
    skills: list[str] | None = []
    description: str | None = None
    responsibilities: list[str] | None = []
    requirements: list[str] | None = []
    benefits: list[str] | None = []
    contact: str | None = None
    apply_url: str | None = None
    ai_job_summary: str | None = None
    required_proposal_questions: list[str] | None = []


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityRead(OpportunityBase):
    id: UUID
    createdAt: datetime
    updatedAt: datetime | None = None

    model_config = {"from_attributes": True}
