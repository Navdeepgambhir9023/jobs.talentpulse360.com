"""Tests for app.events.emitter — JobsEventEmitter."""

from unittest.mock import AsyncMock

import pytest

from app.events.emitter import JobsEventEmitter
from app.events import types
from tests.conftest import make_job_record


@pytest.fixture()
def shared_emitter() -> AsyncMock:
    """Create a mocked shared EventEmitter."""
    emitter = AsyncMock()
    emitter.emit = AsyncMock(return_value="evt_test_001")
    return emitter


@pytest.fixture()
def emitter(shared_emitter) -> JobsEventEmitter:
    """Create a JobsEventEmitter with mocked backend."""
    return JobsEventEmitter(shared_emitter)


class TestJobsEventEmitter:
    """Tests for typed event emission methods."""

    @pytest.mark.asyncio
    async def test_emit_job_created(self, emitter, shared_emitter):
        """emit_job_created calls shared emitter with correct args."""
        job = make_job_record()
        await emitter.emit_job_created(job)

        shared_emitter.emit.assert_called_once()
        call_kwargs = shared_emitter.emit.call_args[1]
        assert call_kwargs["event_type"] == types.JOB_CREATED
        assert call_kwargs["aggregate_id"] == job["id"]
        assert call_kwargs["aggregate_type"] == "job"

    @pytest.mark.asyncio
    async def test_emit_job_published(self, emitter, shared_emitter):
        """emit_job_published calls shared emitter."""
        job = make_job_record({"status": "published", "is_public": True})
        await emitter.emit_job_published(job)

        call_kwargs = shared_emitter.emit.call_args[1]
        assert call_kwargs["event_type"] == types.JOB_PUBLISHED
        assert call_kwargs["payload"]["is_public"] is True

    @pytest.mark.asyncio
    async def test_emit_job_analysis_requested(self, emitter, shared_emitter):
        """emit_job_analysis_requested emits with job id and public id."""
        await emitter.emit_job_analysis_requested(1, "job_01TEST")

        call_kwargs = shared_emitter.emit.call_args[1]
        assert call_kwargs["event_type"] == types.JOB_ANALYSIS_REQUESTED
        assert call_kwargs["aggregate_id"] == 1

    @pytest.mark.asyncio
    async def test_emit_job_closed(self, emitter, shared_emitter):
        """emit_job_closed includes closure reason."""
        job = make_job_record({"closure_reason": "filled"})
        await emitter.emit_job_closed(job)

        call_kwargs = shared_emitter.emit.call_args[1]
        assert call_kwargs["event_type"] == types.JOB_CLOSED
        assert call_kwargs["payload"]["closure_reason"] == "filled"

    @pytest.mark.asyncio
    async def test_emit_weightages_updated(self, emitter, shared_emitter):
        """emit_weightages_updated emits correct event type."""
        await emitter.emit_weightages_updated(1, "job_01TEST")

        call_kwargs = shared_emitter.emit.call_args[1]
        assert call_kwargs["event_type"] == types.JOB_WEIGHTAGES_UPDATED

    @pytest.mark.asyncio
    async def test_emit_qualifications_updated(self, emitter, shared_emitter):
        """emit_qualifications_updated emits correct event type."""
        await emitter.emit_qualifications_updated(1, "job_01TEST")

        call_kwargs = shared_emitter.emit.call_args[1]
        assert call_kwargs["event_type"] == types.JOB_QUALIFICATIONS_UPDATED
