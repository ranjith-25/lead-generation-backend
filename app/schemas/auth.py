from pydantic import BaseModel, EmailStr, Field

from app.schemas.password import Password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    user_id: UUid
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResetPasswordRequest(BaseModel):
    """`token` is the short-lived JWT returned by `/auth/verify-otp`."""

    token: str
    new_password: Password
    confirm_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
