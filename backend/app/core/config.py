from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Driven Red vs Blue Cyber Platform"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = Field(
        ...,
        validation_alias=AliasChoices("JWT_SECRET", "SECRET_KEY"),
    )

    DATABASE_URL: str = Field(
        ...,
        validation_alias=AliasChoices(
            "DATABASE_URL",
            "POSTGRES_URL",
            "DB_URL",
        ),
    )

    DB_ECHO: bool = False
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    MODEL_DIR: str = "../models"
    DATASETS_DIR: str = "../datasets"
    REPORTS_DIR: str = "../reports"

    model_config = SettingsConfigDict(
        env_file=("../.env", "../.env.local"),
        case_sensitive=True,
        extra="ignore",
    )


    def __init__(self, **values):
        super().__init__(**values)
        if not self.SECRET_KEY or not self.SECRET_KEY.strip():
            raise RuntimeError("JWT_SECRET environment variable is required and must not be empty")
        if not self.DATABASE_URL or not self.DATABASE_URL.strip():
            raise RuntimeError("DATABASE_URL environment variable is required and must not be empty")

settings = Settings()
