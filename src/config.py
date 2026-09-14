import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./carepulse_demo.db"
    app_env: str = "demo"
    secret_key: str = "carepulse-demo-only-change-in-production"
    session_ttl_hours: int = 8
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
