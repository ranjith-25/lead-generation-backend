from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.platform import PlatformDTO, PlatformListRead


class GetPlatformResponse(BaseResponse):
    platform: Optional[PlatformDTO] = Field(None, description="Platform")
    platformList: Optional[list[PlatformListRead]] = Field(None, description="Platform List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreatePlatformResponse(BaseResponse):
    newPlatform: PlatformDTO = Field(..., description="New Platform Created")
    status_code: int = Field(200)


class UpdatePlatformResponse(BaseResponse):
    updatedPlatform: PlatformDTO = Field(..., description="Platform Updated")
    status_code: int = Field(200)


class DeletePlatformResponse(BaseResponse):
    status_code: int = Field(200)
