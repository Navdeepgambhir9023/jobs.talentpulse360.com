"""Integration tests for job analysis API endpoints."""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import deps
from app.api.v1.endpoints.job_analysis import router as analysis_router
from tests.conftest import make_analysis_record


def _create_analysis_app() -> FastAPI:
    """Create a minimal app with analysis router."""
    app = FastAPI()
    app.include_router(analysis_router, prefix="/v1")
    return app


class TestAnalysisEndpoints:
    """Tests for /v1/jobs/{id}/analysis endpoints."""

    @pytest.mark.asyncio
    async def test_get_analysis_returns_list(self):
        """GET /v1/jobs/{id}/analysis returns analysis records."""
        mock_service = AsyncMock()
        mock_service.get_analysis.return_value = [make_analysis_record()]

        app = _create_analysis_app()
        app.dependency_overrides[deps.get_job_analysis_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.get("/v1/jobs/job_01TEST/analysis")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 1
        assert data[0]["requirement"] == "5 years Python experience"

    @pytest.mark.asyncio
    async def test_get_analysis_empty(self):
        """GET /v1/jobs/{id}/analysis returns empty list."""
        mock_service = AsyncMock()
        mock_service.get_analysis.return_value = []

        app = _create_analysis_app()
        app.dependency_overrides[deps.get_job_analysis_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.get("/v1/jobs/job_01TEST/analysis")

        assert resp.status_code == 200
        assert resp.json()["data"] == []

    @pytest.mark.asyncio
    async def test_add_requirement_endpoint(self):
        """POST /v1/jobs/{id}/analysis creates a requirement."""
        mock_service = AsyncMock()
        mock_service.add_requirement.return_value = make_analysis_record()

        app = _create_analysis_app()
        app.dependency_overrides[deps.get_job_analysis_service] = lambda: mock_service

        with TestClient(app) as client:
            resp = client.post(
                "/v1/jobs/job_01TEST/analysis",
                json={
                    "requirement": "5 years Python experience",
                    "category": "Work Experience",
                    "distributed_weightage": 15.0,
                },
            )

        assert resp.status_code == 201
        assert resp.json()["data"]["public_id"] == "jan_01TEST"
