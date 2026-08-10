from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.pipeline_execution_status import PipelineExecutionStatusDTO


class GetPipelineExecutionStatusResponse(BaseResponse):
    pipelineExecutionStatus: Optional[PipelineExecutionStatusDTO] = Field(None, description="Pipeline Execution Status")
    pipelineExecutionStatusList: Optional[list[PipelineExecutionStatusDTO]] = Field(None, description="Pipeline Execution Status List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreatePipelineExecutionStatusResponse(BaseResponse):
    newPipelineExecutionStatus: PipelineExecutionStatusDTO = Field(..., description="New Pipeline Execution Status Created")
    status_code: int = Field(200)


class UpdatePipelineExecutionStatusResponse(BaseResponse):
    updatedPipelineExecutionStatus: PipelineExecutionStatusDTO = Field(..., description="Pipeline Execution Status Updated")
    status_code: int = Field(200)


class DeletePipelineExecutionStatusResponse(BaseResponse):
    status_code: int = Field(200)
