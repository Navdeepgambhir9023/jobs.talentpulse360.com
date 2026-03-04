"""Job Analysis Service.

Domain: Jobs
Writes to: job_analysis
Provides business logic for managing AI-extracted job requirements.
"""

import logging
from typing import Any

from tp360_shared.errors.exceptions import NotFoundError

from app.core.exceptions import JobRequirementLimitError
from app.events.emitter import JobsEventEmitter
from app.repositories.job_analysis_repo import JobAnalysisRepository
from app.repositories.job_repo import JobRepository

logger = logging.getLogger(__name__)

MAX_REQUIREMENTS = 100


class JobAnalysisService:
    """Business logic for job analysis requirements."""

    def __init__(
        self,
        job_repo: JobRepository,
        analysis_repo: JobAnalysisRepository,
        event_emitter: JobsEventEmitter,
    ) -> None:
        self._job_repo = job_repo
        self._analysis_repo = analysis_repo
        self._events = event_emitter

    async def get_analysis(self, job_public_id: str) -> list[dict[str, Any]]:
        """Get all analysis requirements for a job.

        Args:
            job_public_id: Job ULID public identifier.

        Returns:
            List of analysis requirement records.

        Raises:
            NotFoundError: If job not found.
        """
        job = await self._job_repo.find_by_public_id(job_public_id)
        if not job:
            raise NotFoundError("Job", job_public_id)
        return await self._analysis_repo.find_by_job_id(job["id"])

    async def add_requirement(
        self, job_public_id: str, data: dict[str, Any],
    ) -> dict[str, Any]:
        """Add a requirement to a job's analysis.

        Args:
            job_public_id: Job ULID public identifier.
            data: Validated requirement data.

        Returns:
            Created analysis record.

        Raises:
            NotFoundError: If job not found.
            JobRequirementLimitError: If limit exceeded.
        """
        job = await self._job_repo.find_by_public_id(job_public_id)
        if not job:
            raise NotFoundError("Job", job_public_id)

        count = await self._analysis_repo.count_by_job_id(job["id"])
        if count >= MAX_REQUIREMENTS:
            raise JobRequirementLimitError(job_public_id, MAX_REQUIREMENTS)

        data["job_id"] = job["id"]
        record = await self._analysis_repo.create(data)
        logger.info(
            "Analysis requirement added",
            extra={"job_id": job["id"], "requirement": data["requirement"]},
        )
        return record
