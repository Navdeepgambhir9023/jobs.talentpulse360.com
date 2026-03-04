"""Tests for app.services.job_qualification_service — Qualification logic."""

from unittest.mock import AsyncMock

import pytest

from tp360_shared.errors.exceptions import NotFoundError

from app.services.job_qualification_service import JobQualificationService
from tests.conftest import make_job_record


@pytest.fixture()
def job_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def qualification_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def event_emitter() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def service(job_repo, qualification_repo, event_emitter) -> JobQualificationService:
    return JobQualificationService(job_repo, qualification_repo, event_emitter)


class TestGetQualifications:
    """Tests for retrieving qualifications."""

    @pytest.mark.asyncio
    async def test_get_qualifications_returns_record(
        self, service, job_repo, qualification_repo,
    ):
        """Returns qualification record."""
        job = make_job_record()
        job_repo.find_by_public_id.return_value = job
        qual_record = {"public_id": "jql_01TEST", "job_id": 1, "country": "US"}
        qualification_repo.find_by_job_id.return_value = qual_record

        result = await service.get_qualifications("job_01TEST")
        assert result["country"] == "US"

    @pytest.mark.asyncio
    async def test_get_qualifications_returns_none(
        self, service, job_repo, qualification_repo,
    ):
        """Returns None when no qualifications exist."""
        job = make_job_record()
        job_repo.find_by_public_id.return_value = job
        qualification_repo.find_by_job_id.return_value = None

        result = await service.get_qualifications("job_01TEST")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_qualifications_job_not_found(self, service, job_repo):
        """Raises NotFoundError if job doesn't exist."""
        job_repo.find_by_public_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_qualifications("job_MISSING")


class TestUpsertQualifications:
    """Tests for creating/updating qualifications."""

    @pytest.mark.asyncio
    async def test_upsert_creates_qualifications(
        self, service, job_repo, qualification_repo, event_emitter,
    ):
        """Upsert creates qualification record."""
        job = make_job_record()
        job_repo.find_by_public_id.return_value = job
        qualification_repo.upsert.return_value = {
            "public_id": "jql_01TEST",
            "job_id": 1,
            "country": "US",
        }

        result = await service.upsert_qualifications(
            "job_01TEST", {"country": "US"},
        )
        assert result["country"] == "US"
        event_emitter.emit_qualifications_updated.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_sets_job_id(
        self, service, job_repo, qualification_repo, event_emitter,
    ):
        """Upsert sets job_id from looked-up job."""
        job = make_job_record({"id": 55})
        job_repo.find_by_public_id.return_value = job
        qualification_repo.upsert.return_value = {"job_id": 55}

        await service.upsert_qualifications("job_01TEST", {"country": "CA"})
        call_data = qualification_repo.upsert.call_args[0][0]
        assert call_data["job_id"] == 55
