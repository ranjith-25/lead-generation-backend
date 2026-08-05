from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.platform import PlatformDTO


class GetPlatformResponse(BaseResponse):
    platform: Optional[PlatformDTO] = Field(None, description="Platform")
    platformList: Optional[list[PlatformDTO]] = Field(None, description="Platform List")
    status_code: int = Field(200)


class CreatePlatformResponse(BaseResponse):
    newPlatform: PlatformDTO = Field(..., description="New Platform Created")
    status_code: int = Field(200)


class UpdatePlatformResponse(BaseResponse):
    updatedPlatform: PlatformDTO = Field(..., description="Platform Updated")
    status_code: int = Field(200)


class DeletePlatformResponse(BaseResponse):
    status_code: int = Field(200)
