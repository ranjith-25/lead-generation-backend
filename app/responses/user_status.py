from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.user_status import UserStatusDTO, UserStatusListRead


class GetUserStatusResponse(BaseResponse):
    userStatus: Optional[UserStatusDTO] = Field(None, description="User Status")
    userStatusList: Optional[list[UserStatusListRead]] = Field(None, description="User Status List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreateUserStatusResponse(BaseResponse):
    newUserStatus: UserStatusDTO = Field(..., description="New User Status Created")
    status_code: int = Field(200)


class UpdateUserStatusResponse(BaseResponse):
    updatedUserStatus: UserStatusDTO = Field(..., description="User Status Updated")
    status_code: int = Field(200)


class DeleteUserStatusResponse(BaseResponse):
    status_code: int = Field(200)
