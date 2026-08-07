from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.branch import BranchDTO


class GetBranchResponse(BaseResponse):
    branch: Optional[BranchDTO] = Field(None, description="Branch")
    branchList: Optional[list[BranchDTO]] = Field(None, description="Branch List")
    status_code: int = Field(200)


class CreateBranchResponse(BaseResponse):
    newBranch: BranchDTO = Field(..., description="New Branch Created")
    status_code: int = Field(200)


class UpdateBranchResponse(BaseResponse):
    updatedBranch: BranchDTO = Field(..., description="Branch Updated")
    status_code: int = Field(200)


class DeleteBranchResponse(BaseResponse):
    status_code: int = Field(200)
