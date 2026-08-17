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
    CASE_STUDY_DIR: str = "uploads/case_studies"

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    OTP_EXPIRE_MINUTES: int = 10

    PASSWORD_RESET_JWT_EXPIRE_MINUTES: int = 10

    FRONTEND_BASE_URL : str

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = ""
    
    DB_LOGS: bool = False

    STREAM_TOKEN_EXPIRE_SECONDS: int = 60
    STREAM_KEEPALIVE_SECONDS: int = 25
    STREAM_SESSION_RECHECK_SECONDS: int = 300

    DB_POOL_SIZE: int = 3
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET : str
    

settings = Settings()
