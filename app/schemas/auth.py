from pydantic import BaseModel, EmailStr, Field

from app.schemas.password import Password
from uuid import UUID

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    user_id: UUID
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResetPasswordRequest(BaseModel):
    user_id: UUID
    new_password: Password
    confirm_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
