"""Tests for app.repositories — Repository classes."""

from unittest.mock import AsyncMock

import pytest

from app.repositories.job_repo import JobRepository
from app.repositories.job_analysis_repo import JobAnalysisRepository
from app.repositories.job_weightage_repo import JobWeightageRepository
from app.repositories.category_weightage_repo import CategoryWeightageRepository
from app.repositories.job_qualification_repo import JobQualificationRepository


class TestJobRepository:
    """Tests for JobRepository."""

    def test_table_name(self):
        repo = JobRepository(AsyncMock())
        assert repo.table_name == "jobs"
        assert repo.entity_prefix == "job"

    @pytest.mark.asyncio
    async def test_find_by_organization(self):
        """find_by_organization returns list of jobs."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetch.return_value = [
            {"id": 1, "public_id": "job_01", "status": "draft"},
        ]

        repo = JobRepository(mock_pool)
        result = await repo.find_by_organization(100)

        assert len(result) == 1
        assert result[0]["public_id"] == "job_01"

    @pytest.mark.asyncio
    async def test_find_by_organization_with_status(self):
        """find_by_organization with status filter."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetch.return_value = []

        repo = JobRepository(mock_pool)
        result = await repo.find_by_organization(100, status="published")

        assert result == []
        call_args = mock_conn.fetch.call_args[0]
        assert "status = $2" in call_args[0]

    @pytest.mark.asyncio
    async def test_update_status(self):
        """update_status delegates to update with status field."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetchrow.return_value = {"id": 1, "status": "published"}

        repo = JobRepository(mock_pool)
        result = await repo.update_status(1, "published")

        assert result is not None


class TestJobAnalysisRepository:
    """Tests for JobAnalysisRepository."""

    def test_table_name(self):
        repo = JobAnalysisRepository(AsyncMock())
        assert repo.table_name == "job_analysis"
        assert repo.entity_prefix == "jan"

    @pytest.mark.asyncio
    async def test_find_by_job_id(self):
        """find_by_job_id returns list of requirements."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetch.return_value = [
            {"id": 1, "requirement": "Python", "is_active": True},
        ]

        repo = JobAnalysisRepository(mock_pool)
        result = await repo.find_by_job_id(1)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_count_by_job_id(self):
        """count_by_job_id returns count."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetchval.return_value = 5

        repo = JobAnalysisRepository(mock_pool)
        result = await repo.count_by_job_id(1)
        assert result == 5


class TestJobWeightageRepository:
    """Tests for JobWeightageRepository."""

    def test_table_name(self):
        repo = JobWeightageRepository(AsyncMock())
        assert repo.table_name == "job_requirement_weightages"
        assert repo.entity_prefix == "jrw"


class TestCategoryWeightageRepository:
    """Tests for CategoryWeightageRepository."""

    def test_table_name(self):
        repo = CategoryWeightageRepository(AsyncMock())
        assert repo.table_name == "category_weightages"
        assert repo.entity_prefix == "cwt"


class TestJobQualificationRepository:
    """Tests for JobQualificationRepository."""

    def test_table_name(self):
        repo = JobQualificationRepository(AsyncMock())
        assert repo.table_name == "job_qualifications"
        assert repo.entity_prefix == "jql"

    @pytest.mark.asyncio
    async def test_find_by_job_id_returns_record(self):
        """find_by_job_id returns single record."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetchrow.return_value = {
            "id": 1, "job_id": 1, "country": "US",
        }

        repo = JobQualificationRepository(mock_pool)
        result = await repo.find_by_job_id(1)
        assert result["country"] == "US"

    @pytest.mark.asyncio
    async def test_find_by_job_id_returns_none(self):
        """find_by_job_id returns None when not found."""
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_conn.fetchrow.return_value = None

        repo = JobQualificationRepository(mock_pool)
        result = await repo.find_by_job_id(999)
        assert result is None
