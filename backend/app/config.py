"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://cenems_user:cenems_pass@localhost:5432/cenems"

    # Logging
    log_level: str = "INFO"

    # Application
    app_name: str = "CenEMS Telemetry Service"
    app_version: str = "1.0.0"

    # Normalization thresholds (for suspicious jump detection)
    max_reasonable_delta: float = 10000.0  # kWh

    class Config:
        env_file = ".env"
        case_sensitive = False


# Single global settings instance
settings = Settings()
