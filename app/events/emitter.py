"""Jobs Event Emitter.

Domain-specific wrapper around tp360_shared.events.emitter.EventEmitter.
Provides typed helper methods for every event the jobs-service emits.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from tp360_shared.events.emitter import EventEmitter

from app.events import types

logger = logging.getLogger(__name__)


class JobsEventEmitter:
    """Typed event emission methods for the jobs domain."""

    def __init__(self, event_emitter: EventEmitter) -> None:
        self._emitter = event_emitter

    async def emit_job_created(self, job: dict[str, Any]) -> None:
        """Emit job.created event after a new job is inserted."""
        await self._emitter.emit(
            event_type=types.JOB_CREATED,
            aggregate_id=job["id"],
            aggregate_type="job",
            payload={
                "public_id": job["public_id"],
                "organization_id": job["organization_id"],
                "title": job["title"],
                "status": job.get("status", "draft"),
            },
        )

    async def emit_job_published(self, job: dict[str, Any]) -> None:
        """Emit job.published event after a job is published."""
        await self._emitter.emit(
            event_type=types.JOB_PUBLISHED,
            aggregate_id=job["id"],
            aggregate_type="job",
            payload={
                "job_public_id": job["public_id"],
                "published_at": datetime.now(timezone.utc).isoformat(),
                "is_public": job.get("is_public", False),
            },
        )

    async def emit_job_analysis_requested(
        self, job_id: int, job_public_id: str,
    ) -> None:
        """Emit job.analysis_requested to trigger AI analysis."""
        await self._emitter.emit(
            event_type=types.JOB_ANALYSIS_REQUESTED,
            aggregate_id=job_id,
            aggregate_type="job",
            payload={"job_public_id": job_public_id},
        )

    async def emit_job_closed(self, job: dict[str, Any]) -> None:
        """Emit job.closed event."""
        await self._emitter.emit(
            event_type=types.JOB_CLOSED,
            aggregate_id=job["id"],
            aggregate_type="job",
            payload={
                "job_public_id": job["public_id"],
                "closure_reason": job.get("closure_reason"),
            },
        )

    async def emit_weightages_updated(
        self, job_id: int, job_public_id: str,
    ) -> None:
        """Emit job.weightages_updated event."""
        await self._emitter.emit(
            event_type=types.JOB_WEIGHTAGES_UPDATED,
            aggregate_id=job_id,
            aggregate_type="job",
            payload={"job_public_id": job_public_id},
        )

    async def emit_qualifications_updated(
        self, job_id: int, job_public_id: str,
    ) -> None:
        """Emit job.qualifications_updated event."""
        await self._emitter.emit(
            event_type=types.JOB_QUALIFICATIONS_UPDATED,
            aggregate_id=job_id,
            aggregate_type="job",
            payload={"job_public_id": job_public_id},
        )
