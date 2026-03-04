"""Tests for app.core — Configuration and exceptions."""

import pytest

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    InvalidJobStatusTransitionError,
    JobAlreadyPublishedError,
    JobNotFoundError,
    JobRequirementLimitError,
)


class TestSettings:
    """Tests for jobs service configuration."""

    def test_default_service_name(self):
        settings = Settings()
        assert settings.SERVICE_NAME == "jobs-service"

    def test_default_port(self):
        settings = Settings()
        assert settings.SERVICE_PORT == 8005

    def test_default_max_requirements(self):
        settings = Settings()
        assert settings.MAX_REQUIREMENTS_PER_JOB == 100

    def test_get_settings_returns_singleton(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


class TestExceptions:
    """Tests for jobs-service-specific exceptions."""

    def test_job_not_found(self):
        exc = JobNotFoundError("job_01TEST")
        assert exc.status_code == 404
        assert exc.code == "JOB_NOT_FOUND"
        assert "job_01TEST" in exc.message

    def test_invalid_status_transition(self):
        exc = InvalidJobStatusTransitionError("draft", "archived")
        assert exc.status_code == 409
        assert "draft" in exc.message
        assert "archived" in exc.message

    def test_job_already_published(self):
        exc = JobAlreadyPublishedError("job_02TEST")
        assert exc.status_code == 409
        assert "job_02TEST" in exc.message

    def test_requirement_limit_error(self):
        exc = JobRequirementLimitError("job_03TEST", 100)
        assert exc.status_code == 400
        assert "100" in exc.message
