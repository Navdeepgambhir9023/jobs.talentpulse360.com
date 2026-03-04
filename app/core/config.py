"""Jobs service configuration.

Extends BaseServiceSettings with jobs-service-specific settings.
All configuration loaded from environment variables.
"""

from functools import lru_cache

from tp360_shared.config.base_settings import BaseServiceSettings


class Settings(BaseServiceSettings):
    """Jobs service settings."""

    SERVICE_NAME: str = "jobs-service"
    SERVICE_PORT: int = 8005

    MAX_REQUIREMENTS_PER_JOB: int = 100
    MAX_CATEGORIES: int = 10
    DEFAULT_QUALIFICATION_THRESHOLD: float = 50.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
