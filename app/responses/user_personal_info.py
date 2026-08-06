from pydantic import BaseModel, Field

from app.responses.base import BaseResponse
from app.schemas.user_personal_info import UserPersonalInfoResponse


class GetUserPersonalInfoResponse(BaseResponse):
    personalInfo: UserPersonalInfoResponse | None = Field(default=None, description="User Personal Info Details")


class CreateUserPersonalInfoResponse(BaseResponse):
    personalInfo: UserPersonalInfoResponse | None = Field(default=None, description="Newly created User Personal Info")


class UpdateUserPersonalInfoResponse(BaseResponse):
    personalInfo: UserPersonalInfoResponse | None = Field(default=None, description="Updated User Personal Info details")


class DeleteUserPersonalInfoResponse(BaseResponse):
    pass
