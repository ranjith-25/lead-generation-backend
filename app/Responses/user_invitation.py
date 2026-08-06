from typing import Optional
from pydantic import Field
from app.responses.base import BaseResponse
from app.schemas.user_invitation import UserInvitationDTO


class GetUserInvitationResponse(BaseResponse):
    userInvitation: Optional[UserInvitationDTO] = Field(None, description="User Invitation")
    userInvitationList: Optional[list[UserInvitationDTO]] = Field(None, description="User Invitation List")
    status_code: int = Field(200)


class CreateUserInvitationResponse(BaseResponse):
    newUserInvitation: UserInvitationDTO = Field(..., description="New User Invitation Created")
    status_code: int = Field(200)


class UpdateUserInvitationResponse(BaseResponse):
    updatedUserInvitation: UserInvitationDTO = Field(..., description="User Invitation Updated")
    status_code: int = Field(200)


class DeleteUserInvitationResponse(BaseResponse):
    status_code: int = Field(200)
