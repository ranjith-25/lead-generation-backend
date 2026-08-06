from pydantic import Field
from typing import Optional

from app.responses.base import BaseResponse
from app.schemas.techstack import TechStackDTO


class GetTechStackResponse(BaseResponse):
    techStack: Optional[TechStackDTO] = Field(None, description="Tech Stack")
    techStackList: Optional[list[TechStackDTO]] = Field(None, description="Tech Stack List")


class CreateTechStackResponse(BaseResponse):
    newTechStack: TechStackDTO = Field(..., description="New Tech Stack Created")


class UpdateTechStackResponse(BaseResponse):
    updatedTechStack: TechStackDTO = Field(..., description="Tech Stack Updated")


class DeleteTechStackResponse(BaseResponse):
    pass
