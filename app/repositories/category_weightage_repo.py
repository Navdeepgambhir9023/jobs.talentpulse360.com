"""Repository for the category_weightages table.

Domain: Jobs
Writes to: category_weightages
Provides CRUD for per-category aggregate scoring weights.
"""

import logging
from typing import Any, Optional

import asyncpg

from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CategoryWeightageRepository(BaseRepository):
    """Database access for the category_weightages table."""

    table_name = "category_weightages"
    entity_prefix = "cwt"

    async def find_by_job_id(
        self,
        job_id: int,
        active_only: bool = True,
        conn: Optional[asyncpg.Connection] = None,
    ) -> list[dict[str, Any]]:
        """Find all category weightages for a job.

        Args:
            job_id: Internal BIGINT job id.
            active_only: Filter to active rows.
            conn: Optional connection for transaction.

        Returns:
            List of category weightage records.
        """
        where = "WHERE job_id = $1"
        if active_only:
            where += " AND is_active = true"
        query = f"SELECT * FROM category_weightages {where} ORDER BY category"
        acquired = await self._get_conn(conn)
        try:
            rows = await acquired.fetch(query, job_id)
            return [dict(r) for r in rows]
        finally:
            await self._release_conn(acquired, conn)
