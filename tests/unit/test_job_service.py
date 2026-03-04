"""Tests for app.services.job_service — Job lifecycle business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from tp360_shared.errors.exceptions import NotFoundError

from app.core.exceptions import InvalidJobStatusTransitionError
from app.services.job_service import JobService
from tests.conftest import make_job_record


@pytest.fixture()
def job_repo() -> AsyncMock:
    """Create a mocked JobRepository."""
    repo = AsyncMock()
    repo._pool = AsyncMock()
    return repo


@pytest.fixture()
def event_emitter() -> AsyncMock:
    """Create a mocked JobsEventEmitter."""
    emitter = AsyncMock()
    return emitter


@pytest.fixture()
def service(job_repo, event_emitter) -> JobService:
    """Create a JobService with mocked dependencies."""
    return JobService(job_repo, event_emitter)


class TestCreateJob:
    """Tests for job creation."""

    @pytest.mark.asyncio
    async def test_create_job_sets_draft_status(self, service, job_repo):
        """New jobs are always created in draft status."""
        record = make_job_record()
        job_repo.create.return_value = record

        result = await service.create_job({"title": "Engineer", "organization_id": 1})

        job_repo.create.assert_called_once()
        call_args = job_repo.create.call_args[0][0]
        assert call_args["status"] == "draft"
        assert result == record

    @pytest.mark.asyncio
    async def test_create_job_emits_event(self, service, job_repo, event_emitter):
        """Job creation emits job.created event."""
        record = make_job_record()
        job_repo.create.return_value = record

        await service.create_job({"title": "Engineer"})

        event_emitter.emit_job_created.assert_called_once_with(record)


class TestGetJob:
    """Tests for job retrieval."""

    @pytest.mark.asyncio
    async def test_get_existing_job(self, service, job_repo):
        """Existing job is returned successfully."""
        record = make_job_record()
        job_repo.find_by_public_id.return_value = record

        result = await service.get_job("job_01TEST")
        assert result["public_id"] == "job_01TEST"

    @pytest.mark.asyncio
    async def test_get_missing_job_raises(self, service, job_repo):
        """Missing job raises NotFoundError."""
        job_repo.find_by_public_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_job("job_MISSING")


class TestUpdateJob:
    """Tests for job updates."""

    @pytest.mark.asyncio
    async def test_update_job_fields(self, service, job_repo):
        """Update applies clean fields."""
        record = make_job_record()
        updated = make_job_record({"title": "Lead Engineer"})
        job_repo.find_by_public_id.return_value = record
        job_repo.update.return_value = updated

        result = await service.update_job("job_01TEST", {"title": "Lead Engineer"})
        assert result["title"] == "Lead Engineer"

    @pytest.mark.asyncio
    async def test_update_with_empty_data_returns_original(self, service, job_repo):
        """Empty update data returns original record."""
        record = make_job_record()
        job_repo.find_by_public_id.return_value = record

        result = await service.update_job("job_01TEST", {})
        assert result == record
        job_repo.update.assert_not_called()


class TestPublishJob:
    """Tests for job publishing."""

    @pytest.mark.asyncio
    async def test_publish_draft_job(self, service, job_repo, event_emitter):
        """Draft job can be published."""
        record = make_job_record({"status": "draft"})
        published = make_job_record({"status": "published"})
        job_repo.find_by_public_id.return_value = record
        job_repo.update_status.return_value = published

        result = await service.publish_job("job_01TEST", is_public=True)
        assert result["status"] == "published"
        event_emitter.emit_job_published.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_closed_job_raises(self, service, job_repo):
        """Cannot publish a closed job."""
        record = make_job_record({"status": "closed"})
        job_repo.find_by_public_id.return_value = record

        with pytest.raises(InvalidJobStatusTransitionError):
            await service.publish_job("job_01TEST")


class TestCloseJob:
    """Tests for job closure."""

    @pytest.mark.asyncio
    async def test_close_published_job(self, service, job_repo, event_emitter):
        """Published job can be closed."""
        record = make_job_record({"status": "published"})
        closed = make_job_record({"status": "closed", "closure_reason": "filled"})
        job_repo.find_by_public_id.return_value = record
        job_repo.update_status.return_value = closed

        result = await service.close_job("job_01TEST", "filled")
        assert result["status"] == "closed"
        event_emitter.emit_job_closed.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_archived_job_raises(self, service, job_repo):
        """Cannot close an archived job."""
        record = make_job_record({"status": "archived"})
        job_repo.find_by_public_id.return_value = record

        with pytest.raises(InvalidJobStatusTransitionError):
            await service.close_job("job_01TEST", "filled")


class TestRequestAnalysis:
    """Tests for analysis request."""

    @pytest.mark.asyncio
    async def test_request_analysis_emits_event(self, service, job_repo, event_emitter):
        """Analysis request emits job.analysis_requested."""
        record = make_job_record()
        job_repo.find_by_public_id.return_value = record

        result = await service.request_analysis("job_01TEST")
        event_emitter.emit_job_analysis_requested.assert_called_once_with(
            record["id"], record["public_id"],
        )
        assert result == record


class TestListJobsByOrg:
    """Tests for listing jobs by organization."""

    @pytest.mark.asyncio
    async def test_list_returns_jobs(self, service, job_repo):
        """List returns all jobs for an org."""
        jobs = [make_job_record(), make_job_record({"id": 2, "public_id": "job_02TEST"})]
        job_repo.find_by_organization.return_value = jobs

        result = await service.list_jobs_by_org(100)
        assert len(result) == 2


class TestStatusTransitions:
    """Tests for status transition validation."""

    def test_valid_transitions(self, service):
        """Valid transitions do not raise."""
        service._validate_transition("draft", "published")
        service._validate_transition("published", "closed")
        service._validate_transition("paused", "published")

    def test_invalid_transition_raises(self, service):
        """Invalid transitions raise error."""
        with pytest.raises(InvalidJobStatusTransitionError):
            service._validate_transition("archived", "published")
