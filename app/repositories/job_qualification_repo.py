"""Repository for the job_qualifications table.

Domain: Jobs
Writes to: job_qualifications
Provides CRUD for per-job qualification criteria.
"""

import logging
from typing import Any, Optional

import asyncpg

from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class JobQualificationRepository(BaseRepository):
    """Database access for the job_qualifications table."""

    table_name = "job_qualifications"
    entity_prefix = "jql"

    async def find_by_job_id(
        self,
        job_id: int,
        conn: Optional[asyncpg.Connection] = None,
    ) -> Optional[dict[str, Any]]:
        """Find qualification criteria for a job.

        Args:
            job_id: Internal BIGINT job id.
            conn: Optional connection for transaction.

        Returns:
            Qualification record or None.
        """
        query = (
            "SELECT * FROM job_qualifications "
            "WHERE job_id = $1 AND is_active = true"
        )
        acquired = await self._get_conn(conn)
        try:
            row = await acquired.fetchrow(query, job_id)
            return dict(row) if row else None
        finally:
            await self._release_conn(acquired, conn)
