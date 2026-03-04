"""Shared response models for the jobs service."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    is_database_connected: bool
