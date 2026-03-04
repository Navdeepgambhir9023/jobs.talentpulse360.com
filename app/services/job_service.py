"""Job Service.

Domain: Jobs
Writes to: jobs
Emits: job.created, job.published, job.closed, job.analysis_requested
"""

import logging
from datetime import datetime, timezone
from typing import Any

from tp360_shared.errors.exceptions import NotFoundError

from app.core.exceptions import (
    InvalidJobStatusTransitionError,
    JobAlreadyPublishedError,
)
from app.events.emitter import JobsEventEmitter
from app.repositories.job_repo import JobRepository

logger = logging.getLogger(__name__)

_VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"published", "closed", "archived"},
    "published": {"paused", "closed"},
    "paused": {"published", "closed", "archived"},
    "closed": {"archived"},
    "archived": set(),
}


class JobService:
    """Business logic for job creation, publishing, and lifecycle."""

    def __init__(
        self,
        job_repo: JobRepository,
        event_emitter: JobsEventEmitter,
    ) -> None:
        self._job_repo = job_repo
        self._events = event_emitter

    async def create_job(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new job in draft status.

        Args:
            data: Validated job creation data.

        Returns:
            Created job record.
        """
        data["status"] = "draft"
        job = await self._job_repo.create(data)
        await self._events.emit_job_created(job)
        logger.info("Job created", extra={"job_id": job["id"]})
        return job

    async def get_job(self, public_id: str) -> dict[str, Any]:
        """Get a job by public_id.

        Args:
            public_id: ULID-based public identifier.

        Returns:
            Job record.

        Raises:
            NotFoundError: If job not found.
        """
        job = await self._job_repo.find_by_public_id(public_id)
        if not job:
            raise NotFoundError("Job", public_id)
        return job

    async def update_job(
        self, public_id: str, data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update job fields.

        Args:
            public_id: ULID-based public identifier.
            data: Fields to update.

        Returns:
            Updated job record.

        Raises:
            NotFoundError: If job not found.
        """
        job = await self.get_job(public_id)
        clean = {k: v for k, v in data.items() if v is not None}
        if not clean:
            return job
        updated = await self._job_repo.update(job["id"], clean)
        return updated

    async def publish_job(
        self, public_id: str, is_public: bool = False,
        public_slug: str | None = None,
    ) -> dict[str, Any]:
        """Publish a job (transition to published status).

        Args:
            public_id: ULID-based public identifier.
            is_public: Whether visible on public board.
            public_slug: URL slug for public board.

        Returns:
            Updated job record.
        """
        job = await self.get_job(public_id)
        self._validate_transition(job["status"], "published")
        now = datetime.now(timezone.utc)
        extra = {"published_at": now, "is_public": is_public}
        if public_slug:
            extra["public_slug"] = public_slug
        updated = await self._job_repo.update_status(
            job["id"], "published", extra,
        )
        await self._events.emit_job_published(updated)
        return updated

    async def close_job(
        self, public_id: str, closure_reason: str,
    ) -> dict[str, Any]:
        """Close a job with a reason.

        Args:
            public_id: ULID-based public identifier.
            closure_reason: Reason for closing.

        Returns:
            Updated job record.
        """
        job = await self.get_job(public_id)
        self._validate_transition(job["status"], "closed")
        now = datetime.now(timezone.utc)
        updated = await self._job_repo.update_status(
            job["id"], "closed",
            {"closure_reason": closure_reason, "closed_at": now},
        )
        await self._events.emit_job_closed(updated)
        return updated

    async def request_analysis(self, public_id: str) -> dict[str, Any]:
        """Request AI analysis for a job.

        Args:
            public_id: ULID-based public identifier.

        Returns:
            Job record.
        """
        job = await self.get_job(public_id)
        await self._events.emit_job_analysis_requested(
            job["id"], job["public_id"],
        )
        return job

    async def list_jobs_by_org(
        self, org_id: int, status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List jobs for an organization.

        Args:
            org_id: Internal BIGINT org id.
            status: Optional status filter.

        Returns:
            List of job records.
        """
        return await self._job_repo.find_by_organization(org_id, status)

    def _validate_transition(self, current: str, target: str) -> None:
        """Validate a job status transition."""
        allowed = _VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidJobStatusTransitionError(current, target)
