from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.pipeline_opportunity_project import PipelineOpportunityProjectDTO


class GetPipelineOpportunityProjectResponse(BaseResponse):
    pipelineOpportunityProject: Optional[PipelineOpportunityProjectDTO] = Field(None, description="Pipeline Opportunity Project")
    pipelineOpportunityProjectList: Optional[list[PipelineOpportunityProjectDTO]] = Field(None, description="Pipeline Opportunity Project List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreatePipelineOpportunityProjectResponse(BaseResponse):
    newPipelineOpportunityProject: PipelineOpportunityProjectDTO = Field(..., description="New Pipeline Opportunity Project Created")
    status_code: int = Field(200)


class UpdatePipelineOpportunityProjectResponse(BaseResponse):
    updatedPipelineOpportunityProject: PipelineOpportunityProjectDTO = Field(..., description="Pipeline Opportunity Project Updated")
    status_code: int = Field(200)


class DeletePipelineOpportunityProjectResponse(BaseResponse):
    status_code: int = Field(200)
