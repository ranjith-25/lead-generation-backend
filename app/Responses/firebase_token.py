from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.firebase_token import FirebaseTokenDTO


class GetFirebaseTokenResponse(BaseResponse):
    firebaseToken: Optional[FirebaseTokenDTO] = Field(None, description="Firebase Token")
    firebaseTokenList: Optional[list[FirebaseTokenDTO]] = Field(None, description="Firebase Token List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreateFirebaseTokenResponse(BaseResponse):
    newFirebaseToken: FirebaseTokenDTO = Field(..., description="New Firebase Token Created")
    status_code: int = Field(200)


class UpdateFirebaseTokenResponse(BaseResponse):
    updatedFirebaseToken: FirebaseTokenDTO = Field(..., description="Firebase Token Updated")
    status_code: int = Field(200)


class DeleteFirebaseTokenResponse(BaseResponse):
    status_code: int = Field(200)
