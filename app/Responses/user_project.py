from pydantic import BaseModel, Field
from app.responses.base import BaseResponse
from app.schemas.user_project import UserProjectDTO, UserProjectDetailDTO


class GetUserProjectResponse(BaseResponse):
    userProjectList: list[UserProjectDetailDTO] | None = Field(default=None, description="List of User Projects")
    userProject: UserProjectDetailDTO | None = Field(default=None, description="User Project Details")


class CreateUserProjectResponse(BaseResponse):
    newUserProject: UserProjectDTO | None = Field(default=None, description="Newly created User Project")


class UpdateUserProjectResponse(BaseResponse):
    updatedUserProject: UserProjectDTO | None = Field(default=None, description="Updated User Project details")


class DeleteUserProjectResponse(BaseResponse):
    pass


class UserProjectConfigurationsData(BaseModel):
    projects: list[str] = Field(default_factory=list, description="Project Names")
    roles: list[str] = Field(default_factory=list, description="Job Role Names")
    techstacks: list[str] = Field(default_factory=list, description="Techstack Names")


class UserProjectConfigurationsResponse(BaseResponse):
    data: UserProjectConfigurationsData = Field(..., description="User Project Configurations")