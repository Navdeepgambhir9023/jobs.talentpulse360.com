"""Exception-to-HTTP mapping for jobs service.

Registers jobs-specific exception handlers on the FastAPI app.
Uses tp360_shared global handlers plus any service-specific overrides.
"""

from fastapi import FastAPI

from tp360_shared.errors.handlers import register_exception_handlers


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the jobs service."""
    register_exception_handlers(app)
