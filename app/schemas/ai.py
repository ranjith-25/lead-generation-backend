from pydantic import BaseModel,Field
from uuid import UUID
from typing import Optional

from app.schemas.project import AIProjectRequest

class AIRequestBase(BaseModel):
    user_id: UUID = Field(...,description="The User ID of the user making the request")
    action: str = Field(...,description="The action to be performed by the AI")

class AIGetRelaventProfilesRequest(AIRequestBase):
    job_details : str = Field(...,description="The JobDetails in JSOn string format")
    top_project_ids : list[str] = Field(...,description="List of project ID's erturned form getting relavent projects step")

class AIManualJDRequest(AIRequestBase):
    company_name: str = Field(...,description="The Company Name")
    company_website: str = Field(...,description="The Company Website")
    job_title: str = Field(...,description="The Job Title")
    experience: str = Field(...,description="The Experience")
    job_description: str = Field(...,description="The Job Description")
    additional_notes: Optional[str] = Field(None,description="The Additional Notes")


class AITechnicalPreperationRequest(AIRequestBase):
    job_details: str = Field(...,description="The JobDetails in JSON string format")
    variant_id: str = Field(...,description="The Variant ID")
    matching_skills: list[str] = Field(...,description="List of matching skills")
    missing_skills: list[str] = Field(...,description="List of missing skills")

class AIURLScrapeRequest(AIRequestBase):
    url: str = Field(...,description="The URL to scrape for job details")
    job_roles : list[str] = Field(...,description="List of job roles to scrape for")

class AIGetRelevantProjectsRequest(AIRequestBase):
    job_details: dict = Field(..., description="The job details in JSON format")

class AISalesEnablementRequest(AIRequestBase):
    job_details: dict
    projects: list[AIProjectRequest]