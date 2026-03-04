"""Job Qualification Service.

Domain: Jobs
Writes to: job_qualifications
Provides business logic for managing job qualification criteria.
"""

import logging
from typing import Any, Optional

from tp360_shared.errors.exceptions import NotFoundError

from app.events.emitter import JobsEventEmitter
from app.repositories.job_qualification_repo import JobQualificationRepository
from app.repositories.job_repo import JobRepository

logger = logging.getLogger(__name__)


class JobQualificationService:
    """Business logic for job qualification criteria."""

    def __init__(
        self,
        job_repo: JobRepository,
        qualification_repo: JobQualificationRepository,
        event_emitter: JobsEventEmitter,
    ) -> None:
        self._job_repo = job_repo
        self._qualification_repo = qualification_repo
        self._events = event_emitter

    async def get_qualifications(
        self, job_public_id: str,
    ) -> Optional[dict[str, Any]]:
        """Get qualification criteria for a job.

        Args:
            job_public_id: Job ULID public identifier.

        Returns:
            Qualification record or None.

        Raises:
            NotFoundError: If job not found.
        """
        job = await self._job_repo.find_by_public_id(job_public_id)
        if not job:
            raise NotFoundError("Job", job_public_id)
        return await self._qualification_repo.find_by_job_id(job["id"])

    async def upsert_qualifications(
        self, job_public_id: str, data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update qualification criteria for a job.

        Args:
            job_public_id: Job ULID public identifier.
            data: Validated qualification data.

        Returns:
            Created or updated qualification record.

        Raises:
            NotFoundError: If job not found.
        """
        job = await self._job_repo.find_by_public_id(job_public_id)
        if not job:
            raise NotFoundError("Job", job_public_id)

        data["job_id"] = job["id"]
        record = await self._qualification_repo.upsert(
            data, conflict_columns=["job_id"],
        )
        await self._events.emit_qualifications_updated(
            job["id"], job["public_id"],
        )
        logger.info(
            "Qualifications upserted",
            extra={"job_id": job["id"]},
        )
        return record
