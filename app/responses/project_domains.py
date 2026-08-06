from pydantic import BaseModel,Field
from app.schemas.project_domains import ProjectDomainDTO
from typing import Optional
from app.responses.base import BaseResponse
class GetProjectDomainResponse(BaseResponse):
    projectDomain : Optional[ProjectDomainDTO] = Field(None, description="Project Domain")
    projectDomainList : Optional[list[ProjectDomainDTO]] = Field(None, description="Project Domain List")

class CreateProjectDomainResponse(BaseResponse):
    newProjectDomain : ProjectDomainDTO = Field(...,description="New Project Domain Created")

class UpdateProjectDomainResponse(BaseResponse):
    updatedProjectDomain : ProjectDomainDTO = Field(...,description="Project Domain Updated")

class DeleteProjectDomainResponse(BaseResponse):
    pass
