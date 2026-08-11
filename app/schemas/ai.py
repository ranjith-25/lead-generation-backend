from pydantic import BaseModel,Field
from uuid import UUID
from typing import Optional

class AIGetRelaventProfilesRequest(BaseModel):
    job_details : str = Field(...,description="The JobDetails in JSOn string format")
    top_project_ids : list[str] = Field(...,description="List of project ID's erturned form getting relavent projects step")

class AIManualJDRequest(BaseModel):
    company_name: str = Field(...,description="The Company Name")
    company_website: str = Field(...,description="The Company Website")
    job_title: str = Field(...,description="The Job Title")
    experience: str = Field(...,description="The Experience")
    job_description: str = Field(...,description="The Job Description")
    additional_notes: Optional[str] = Field(None,description="The Additional Notes")
