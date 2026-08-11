from pydantic import BaseModel,Field
from uuid import UUID

class AIGetRelaventProfilesRequest(BaseModel):
    job_details : str = Field(...,description="The JobDetails in JSOn string format")
    top_project_ids : list[str] = Field(...,description="List of project ID's erturned form getting relavent projects step")
