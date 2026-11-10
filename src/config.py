import os
from pydantic_settings import BaseSettings, SettingsConfigDict

DEMO_SECRET_KEY = "carepulse-demo-only-change-in-production"

class Settings(BaseSettings):
    database_url: str = "sqlite:///./carepulse_demo.db"
    app_env: str = "demo"
    secret_key: str = DEMO_SECRET_KEY
    session_ttl_hours: int = 8
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


def validate_runtime_settings():
    if settings.app_env == "production":
        if settings.secret_key == DEMO_SECRET_KEY or len(settings.secret_key) < 32:
            raise RuntimeError(
                "Production requires a unique SECRET_KEY of at least 32 characters."
            )
