"""Tests for app.services.job_analysis_service — Analysis business logic."""

from unittest.mock import AsyncMock

import pytest

from tp360_shared.errors.exceptions import NotFoundError

from app.core.exceptions import JobRequirementLimitError
from app.services.job_analysis_service import JobAnalysisService
from tests.conftest import make_analysis_record, make_job_record


@pytest.fixture()
def job_repo() -> AsyncMock:
    repo = AsyncMock()
    repo._pool = AsyncMock()
    return repo


@pytest.fixture()
def analysis_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def event_emitter() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def service(job_repo, analysis_repo, event_emitter) -> JobAnalysisService:
    return JobAnalysisService(job_repo, analysis_repo, event_emitter)


class TestGetAnalysis:
    """Tests for retrieving analysis requirements."""

    @pytest.mark.asyncio
    async def test_get_analysis_returns_list(self, service, job_repo, analysis_repo):
        """Returns list of analysis records."""
        job = make_job_record()
        job_repo.find_by_public_id.return_value = job
        analysis_repo.find_by_job_id.return_value = [make_analysis_record()]

        result = await service.get_analysis("job_01TEST")
        assert len(result) == 1
        assert result[0]["requirement"] == "5 years Python experience"

    @pytest.mark.asyncio
    async def test_get_analysis_job_not_found(self, service, job_repo):
        """Raises NotFoundError if job doesn't exist."""
        job_repo.find_by_public_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_analysis("job_MISSING")


class TestAddRequirement:
    """Tests for adding analysis requirements."""

    @pytest.mark.asyncio
    async def test_add_requirement_success(self, service, job_repo, analysis_repo):
        """Adds requirement when under limit."""
        job = make_job_record()
        record = make_analysis_record()
        job_repo.find_by_public_id.return_value = job
        analysis_repo.count_by_job_id.return_value = 5
        analysis_repo.create.return_value = record

        result = await service.add_requirement("job_01TEST", {
            "requirement": "5 years Python experience",
            "category": "Work Experience",
        })
        assert result["requirement"] == "5 years Python experience"

    @pytest.mark.asyncio
    async def test_add_requirement_exceeds_limit(self, service, job_repo, analysis_repo):
        """Raises error when requirement limit is exceeded."""
        job = make_job_record()
        job_repo.find_by_public_id.return_value = job
        analysis_repo.count_by_job_id.return_value = 100

        with pytest.raises(JobRequirementLimitError):
            await service.add_requirement("job_01TEST", {
                "requirement": "test",
                "category": "Work Experience",
            })

    @pytest.mark.asyncio
    async def test_add_requirement_sets_job_id(self, service, job_repo, analysis_repo):
        """Sets job_id from the looked-up job."""
        job = make_job_record({"id": 42})
        record = make_analysis_record({"job_id": 42})
        job_repo.find_by_public_id.return_value = job
        analysis_repo.count_by_job_id.return_value = 0
        analysis_repo.create.return_value = record

        await service.add_requirement("job_01TEST", {
            "requirement": "test",
            "category": "Work Experience",
        })
        call_data = analysis_repo.create.call_args[0][0]
        assert call_data["job_id"] == 42
