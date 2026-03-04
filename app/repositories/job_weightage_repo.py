"""Repository for the job_requirement_weightages table.

Domain: Jobs
Writes to: job_requirement_weightages
Provides CRUD for per-requirement distributed weights.
"""

import logging
from typing import Any, Optional

import asyncpg

from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class JobWeightageRepository(BaseRepository):
    """Database access for the job_requirement_weightages table."""

    table_name = "job_requirement_weightages"
    entity_prefix = "jrw"

    async def find_by_job_id(
        self,
        job_id: int,
        active_only: bool = True,
        conn: Optional[asyncpg.Connection] = None,
    ) -> list[dict[str, Any]]:
        """Find all weightages for a job.

        Args:
            job_id: Internal BIGINT job id.
            active_only: Filter to active rows.
            conn: Optional connection for transaction.

        Returns:
            List of weightage records.
        """
        where = "WHERE job_id = $1"
        if active_only:
            where += " AND is_active = true"
        query = (
            f"SELECT * FROM job_requirement_weightages "
            f"{where} ORDER BY category, created_at"
        )
        acquired = await self._get_conn(conn)
        try:
            rows = await acquired.fetch(query, job_id)
            return [dict(r) for r in rows]
        finally:
            await self._release_conn(acquired, conn)
