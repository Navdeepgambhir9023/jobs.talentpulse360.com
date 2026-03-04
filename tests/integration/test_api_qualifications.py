"""Integration tests for job qualifications API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import deps
from app.api.v1.endpoints.job_qualifications import router as qual_router


def _make_qualification_record() -> dict:
    """Create a sample qualification record."""
    now = datetime.now(timezone.utc)
    return {
        "public_id": "jql_01TEST",
        "country": "US",
        "state": "CA",
        "city": "San Francisco",
        "location_flexibility": "hybrid",
        "min_salary": 120000.0,
        "max_salary": 180000.0,
        "salary_currency": "USD",
        "employment_types": ["full_time"],
        "work_arrangements": ["hybrid"],
        "travel_required": False,
        "visa_sponsorship": False,
        "timezone": "America/Los_Angeles",
        "qualification_threshold": 50.0,
        "auto_qualification_enabled": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }


def _create_qual_app() -> FastAPI:
    """Create a minimal app with qualifications router."""
    app = FastAPI()
    app.include_router(qual_router, prefix="/v1")
    return app


class TestQualificationEndpoints:
    """Tests for /v1/jobs/{id}/qualifications endpoints."""

    @pytest.mark.asyncio
    async def test_get_qualifications_returns_record(self):
        """GET returns qualification criteria."""
        mock_service = AsyncMock()
        mock_service.get_qualifications.return_value = _make_qualification_record()

        app = _create_qual_app()
        app.dependency_overrides[deps.get_job_qualification_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.get("/v1/jobs/job_01TEST/qualifications")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["public_id"] == "jql_01TEST"
        assert data["country"] == "US"

    @pytest.mark.asyncio
    async def test_get_qualifications_returns_empty(self):
        """GET returns empty data when no qualifications exist."""
        mock_service = AsyncMock()
        mock_service.get_qualifications.return_value = None

        app = _create_qual_app()
        app.dependency_overrides[deps.get_job_qualification_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.get("/v1/jobs/job_01TEST/qualifications")

        assert resp.status_code == 200
        assert resp.json()["data"] == {}

    @pytest.mark.asyncio
    async def test_upsert_qualifications(self):
        """PUT creates/updates qualification criteria."""
        mock_service = AsyncMock()
        mock_service.upsert_qualifications.return_value = _make_qualification_record()

        app = _create_qual_app()
        app.dependency_overrides[deps.get_job_qualification_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.put(
                "/v1/jobs/job_01TEST/qualifications",
                json={
                    "country": "US",
                    "state": "CA",
                    "min_salary": 120000.0,
                    "max_salary": 180000.0,
                },
            )

        assert resp.status_code == 200
        assert resp.json()["data"]["public_id"] == "jql_01TEST"
