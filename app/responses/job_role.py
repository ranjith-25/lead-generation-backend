from pydantic import BaseModel, Field

from app.responses.base import BaseResponse
from app.schemas.job_role import JobRoleDTO


class GetJobRoleResponse(BaseResponse):
    jobRoleList: list[JobRoleDTO] | None = Field(default=None, description="List of Job Roles")
    jobRole: JobRoleDTO | None = Field(default=None, description="Job Role Details")


class CreateJobRoleResponse(BaseResponse):
    newJobRole: JobRoleDTO | None = Field(default=None, description="Newly created Job Role")


class UpdateJobRoleResponse(BaseResponse):
    updatedJobRole: JobRoleDTO | None = Field(default=None, description="Updated Job Role details")


class DeleteJobRoleResponse(BaseResponse):
    pass
