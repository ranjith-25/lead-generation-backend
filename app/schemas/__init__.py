from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.schemas.user_personal_info import (
    UserPersonalInfoCreate,
    UserPersonalInfoUpdate,
    UserPersonalInfoResponse,
)
from app.schemas.opportunity import OpportunityCreate, OpportunityRead
from app.schemas.profile_variant import ProfileVariantCreate, ProfileVariantUpdate, ProfileVariantDTO

__all__ = [
    "UserCreate",
    "UserRead",
    "UserPersonalInfoCreate",
    "UserPersonalInfoUpdate",
    "UserPersonalInfoResponse",
    "LoginRequest",
    "Token",
    "OpportunityCreate",
    "OpportunityRead",
    "ProfileVariantCreate",
    "ProfileVariantUpdate",
    "ProfileVariantDTO",
]

