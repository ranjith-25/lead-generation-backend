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

settings = Settings()
