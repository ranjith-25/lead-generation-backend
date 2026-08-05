from pydantic import BaseModel, Field
from app.schemas.job_roles import JobRolesDTO
from typing import Optional
from app.responses.base import BaseResponse


class GetJobRolesResponse(BaseResponse):
    jobRole: Optional[JobRolesDTO] = Field(None, description="Job Role")
    jobRoleList: Optional[list[JobRolesDTO]] = Field(None, description="Job Role List")
    status_code: Optional[int] = Field(None, description="Status code")


class CreateJobRolesResponse(BaseResponse):
    newJobRole: JobRolesDTO = Field(..., description="New Job Role Created")
    status_code: Optional[int] = Field(None, description="Status code")


class UpdateJobRolesResponse(BaseResponse):
    updatedJobRole: JobRolesDTO = Field(..., description="Job Role Updated")
    status_code: Optional[int] = Field(None, description="Status code")


class DeleteJobRolesResponse(BaseResponse):
    status_code: Optional[int] = Field(None, description="Status code")
