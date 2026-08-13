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
    
    DB_LOGS: bool = False

    # EventSource cannot set an Authorization header, so the notification stream is opened
    # with a token in the query string. Keep the window short enough that the copy left
    # behind in an access log or a proxy cache is worthless by the time anyone reads it.
    STREAM_TOKEN_EXPIRE_SECONDS: int = 60
    # Comment frames stop proxies culling an idle stream, and the write that fails is how
    # a browser that vanished without a FIN gets noticed.
    STREAM_KEEPALIVE_SECONDS: int = 25
    # How often an already-open stream re-checks that its session survives — this is what
    # makes logout close the connection instead of leaving it fed until the tab dies.
    STREAM_SESSION_RECHECK_SECONDS: int = 300

    # Connection pool ceiling for this process: DB_POOL_SIZE + DB_MAX_OVERFLOW.
    # Keep (ceiling * number of app processes) well under the server's
    # max_connections, and leave headroom for Alembic and DB clients.
    DB_POOL_SIZE: int = 3
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30
    # Drop connections older than this so half-dead backends don't accumulate.
    DB_POOL_RECYCLE: int = 1800

settings = Settings()
