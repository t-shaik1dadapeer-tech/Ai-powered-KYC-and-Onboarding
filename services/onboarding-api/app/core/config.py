from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "onboarding-api"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite:///./onboarding.db"
    pan_verify_mode: str = "mock"
    bank_verify_mode: str = "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
