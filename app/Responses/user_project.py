from pydantic import Field
from app.responses.base import BaseResponse
from app.schemas.user_project import UserProjectDTO


class GetUserProjectResponse(BaseResponse):
    userProjectList: list[UserProjectDTO] | None = Field(default=None, description="List of User Projects")
    userProject: UserProjectDTO | None = Field(default=None, description="User Project Details")


class CreateUserProjectResponse(BaseResponse):
    newUserProject: UserProjectDTO | None = Field(default=None, description="Newly created User Project")


class UpdateUserProjectResponse(BaseResponse):
    updatedUserProject: UserProjectDTO | None = Field(default=None, description="Updated User Project details")


class DeleteUserProjectResponse(BaseResponse):
    pass