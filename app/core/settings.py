from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    ENVIRONMENT: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    AI_BASE_URL : str

    MAX_CASE_STUDY_SIZE_MB: int = 10
    CASE_STUDY_DIR: str = "case_studies"

    # short on purpose: a reset link is a bearer credential sitting in an inbox
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # OTP lifetime for the password reset flow (minutes)
    OTP_EXPIRE_MINUTES: int = 10

    # Reset-token JWT lifetime (issued by /auth/verify-otp, minutes)
    PASSWORD_RESET_JWT_EXPIRE_MINUTES: int = 10

    FRONTEND_BASE_URL : str

    # SMTP — leave SMTP_HOST empty to fall back to console logging (DEV only)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = ""

settings = Settings()
