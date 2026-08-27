from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.pipeline_opportunity_resource import PipelineOpportunityResourceDTO


class GetPipelineOpportunityResourceResponse(BaseResponse):
    pipelineOpportunityResource: Optional[PipelineOpportunityResourceDTO] = Field(None, description="Pipeline Opportunity Resource")
    pipelineOpportunityResourceList: Optional[list[PipelineOpportunityResourceDTO]] = Field(None, description="Pipeline Opportunity Resource List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreatePipelineOpportunityResourceResponse(BaseResponse):
    newPipelineOpportunityResource: PipelineOpportunityResourceDTO = Field(..., description="New Pipeline Opportunity Resource Created")
    status_code: int = Field(200)


class UpdatePipelineOpportunityResourceResponse(BaseResponse):
    updatedPipelineOpportunityResource: PipelineOpportunityResourceDTO = Field(..., description="Pipeline Opportunity Resource Updated")
    status_code: int = Field(200)

class SelectPipelineOpportunityResourcesResponse(BaseResponse):
    selectedPipelineOpportunityResources: list[PipelineOpportunityResourceDTO] = Field(..., description="Pipeline Opportunity Resources Selected")
    status_code: int = Field(200)

class AssignPipelineOpportunityResourcesResponse(BaseResponse):
    assignedPipelineOpportunityResources: list[PipelineOpportunityResourceDTO] = Field(..., description="Pipeline Opportunity Resources Assigned")
    status_code: int = Field(200)

class DeletePipelineOpportunityResourceResponse(BaseResponse):
    status_code: int = Field(200)
