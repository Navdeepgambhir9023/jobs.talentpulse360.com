"""Repository for the job_analysis table.

Domain: Jobs
Writes to: job_analysis
Provides CRUD for AI-extracted job requirements.
"""

import logging
from typing import Any, Optional

import asyncpg

from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class JobAnalysisRepository(BaseRepository):
    """Database access for the job_analysis table."""

    table_name = "job_analysis"
    entity_prefix = "jan"

    async def find_by_job_id(
        self,
        job_id: int,
        active_only: bool = True,
        conn: Optional[asyncpg.Connection] = None,
    ) -> list[dict[str, Any]]:
        """Find all analysis requirements for a job.

        Args:
            job_id: Internal BIGINT job id.
            active_only: Filter to active rows only.
            conn: Optional connection for transaction.

        Returns:
            List of analysis requirement records.
        """
        where = "WHERE job_id = $1"
        if active_only:
            where += " AND is_active = true"
        query = f"SELECT * FROM job_analysis {where} ORDER BY created_at"
        acquired = await self._get_conn(conn)
        try:
            rows = await acquired.fetch(query, job_id)
            return [dict(r) for r in rows]
        finally:
            await self._release_conn(acquired, conn)

    async def count_by_job_id(
        self, job_id: int, conn: Optional[asyncpg.Connection] = None,
    ) -> int:
        """Count active analysis rows for a job.

        Args:
            job_id: Internal BIGINT job id.
            conn: Optional connection for transaction.

        Returns:
            Number of active analysis records.
        """
        query = (
            "SELECT COUNT(*) FROM job_analysis "
            "WHERE job_id = $1 AND is_active = true"
        )
        acquired = await self._get_conn(conn)
        try:
            return await acquired.fetchval(query, job_id)
        finally:
            await self._release_conn(acquired, conn)
