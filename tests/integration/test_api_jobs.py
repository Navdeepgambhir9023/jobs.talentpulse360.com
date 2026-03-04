"""Integration tests for jobs API endpoints using TestClient."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_job_record


def _create_test_app():
    """Create app with mocked lifespan resources."""
    from app.core.config import Settings

    with patch("app.core.config.get_settings") as mock_settings:
        mock_settings.return_value = Settings()
        from app.api.v1.endpoints.jobs import router as jobs_router
        from app.api.v1.endpoints.health import router as health_router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(jobs_router, prefix="/v1")
        app.include_router(health_router)
        return app


class TestJobsEndpoints:
    """Tests for /v1/jobs endpoints."""

    @pytest.mark.asyncio
    async def test_create_job_endpoint(self):
        """POST /v1/jobs creates a job and returns 201."""
        from app.api import deps

        record = make_job_record()
        mock_service = AsyncMock()
        mock_service.create_job.return_value = record

        app = _create_test_app()
        app.dependency_overrides[deps.get_job_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.post("/v1/jobs", json={
                "organization_public_id": "org_01TEST",
                "title": "Senior Engineer",
            })

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["public_id"] == "job_01TEST"

    @pytest.mark.asyncio
    async def test_get_job_endpoint(self):
        """GET /v1/jobs/{id} returns a job."""
        from app.api import deps

        record = make_job_record()
        mock_service = AsyncMock()
        mock_service.get_job.return_value = record

        app = _create_test_app()
        app.dependency_overrides[deps.get_job_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.get("/v1/jobs/job_01TEST")

        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Senior Engineer"

    @pytest.mark.asyncio
    async def test_update_job_endpoint(self):
        """PATCH /v1/jobs/{id} updates fields."""
        from app.api import deps

        updated = make_job_record({"title": "Lead Engineer"})
        mock_service = AsyncMock()
        mock_service.update_job.return_value = updated

        app = _create_test_app()
        app.dependency_overrides[deps.get_job_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.patch("/v1/jobs/job_01TEST", json={"title": "Lead Engineer"})

        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Lead Engineer"

    @pytest.mark.asyncio
    async def test_publish_job_endpoint(self):
        """POST /v1/jobs/{id}/publish transitions to published."""
        from app.api import deps

        published = make_job_record({"status": "published"})
        mock_service = AsyncMock()
        mock_service.publish_job.return_value = published

        app = _create_test_app()
        app.dependency_overrides[deps.get_job_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.post("/v1/jobs/job_01TEST/publish", json={"is_public": True})

        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "published"

    @pytest.mark.asyncio
    async def test_close_job_endpoint(self):
        """POST /v1/jobs/{id}/close transitions to closed."""
        from app.api import deps

        closed = make_job_record({"status": "closed"})
        mock_service = AsyncMock()
        mock_service.close_job.return_value = closed

        app = _create_test_app()
        app.dependency_overrides[deps.get_job_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.post(
                "/v1/jobs/job_01TEST/close",
                json={"closure_reason": "filled"},
            )

        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "closed"

    @pytest.mark.asyncio
    async def test_request_analysis_endpoint(self):
        """POST /v1/jobs/{id}/request-analysis triggers analysis."""
        from app.api import deps

        record = make_job_record()
        mock_service = AsyncMock()
        mock_service.request_analysis.return_value = record

        app = _create_test_app()
        app.dependency_overrides[deps.get_job_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.post("/v1/jobs/job_01TEST/request-analysis")

        assert resp.status_code == 200
