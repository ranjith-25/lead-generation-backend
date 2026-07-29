from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://user:12345678@localhost:5432/lead_generation"
    database_url_sync: str = "postgresql://user:password@localhost:5432/lead_generation"


settings = Settings()
