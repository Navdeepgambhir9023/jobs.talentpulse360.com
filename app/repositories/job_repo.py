"""Repository for the jobs table.

Domain: Jobs
Writes to: jobs
Provides CRUD and lookup operations for job records.
"""

import logging
from typing import Any, Optional

import asyncpg

from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class JobRepository(BaseRepository):
    """Database access for the jobs table."""

    table_name = "jobs"
    entity_prefix = "job"

    async def find_by_organization(
        self,
        organization_id: int,
        status: Optional[str] = None,
        conn: Optional[asyncpg.Connection] = None,
    ) -> list[dict[str, Any]]:
        """Find jobs belonging to an organization.

        Args:
            organization_id: Internal BIGINT org id.
            status: Optional status filter.
            conn: Optional connection for transaction.

        Returns:
            List of job records.
        """
        if status:
            query = (
                "SELECT * FROM jobs "
                "WHERE organization_id = $1 AND status = $2 "
                "ORDER BY created_at DESC"
            )
            params = (organization_id, status)
        else:
            query = (
                "SELECT * FROM jobs "
                "WHERE organization_id = $1 "
                "ORDER BY created_at DESC"
            )
            params = (organization_id,)

        acquired = await self._get_conn(conn)
        try:
            rows = await acquired.fetch(query, *params)
            return [dict(r) for r in rows]
        finally:
            await self._release_conn(acquired, conn)

    async def update_status(
        self,
        job_id: int,
        status: str,
        extra_fields: Optional[dict[str, Any]] = None,
        conn: Optional[asyncpg.Connection] = None,
    ) -> Optional[dict[str, Any]]:
        """Update job status with optional extra fields.

        Args:
            job_id: Internal BIGINT id.
            status: New status value.
            extra_fields: Additional columns to update.
            conn: Optional connection for transaction.

        Returns:
            Updated job record or None.
        """
        data = {"status": status}
        if extra_fields:
            data.update(extra_fields)
        return await self.update(job_id, data, conn=conn)
