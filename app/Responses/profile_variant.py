from pydantic import BaseModel, Field
from app.responses.base import BaseResponse
from app.schemas.profile_variant import ProfileVariantDTO


class GetProfileVariantResponse(BaseResponse):
    profileVariantList: list[ProfileVariantDTO] | None = Field(default=None, description="List of Profile Variants")
    profileVariant: ProfileVariantDTO | None = Field(default=None, description="Profile Variant Details")


class CreateProfileVariantResponse(BaseResponse):
    newProfileVariant: ProfileVariantDTO | None = Field(default=None, description="Newly created Profile Variant")


class UpdateProfileVariantResponse(BaseResponse):
    updatedProfileVariant: ProfileVariantDTO | None = Field(default=None, description="Updated Profile Variant details")


class DeleteProfileVariantResponse(BaseResponse):
    pass