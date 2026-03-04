"""Jobs service test configuration and shared fixtures.

Provides mocked asyncpg pools, connections, Redis clients,
event emitters, and common test data factories.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.events.emitter import JobsEventEmitter


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def mock_pool() -> AsyncMock:
    """Create a mocked asyncpg connection pool."""
    pool = AsyncMock()
    pool.acquire = AsyncMock()
    pool.release = AsyncMock()
    pool.close = AsyncMock()
    pool.fetchval = AsyncMock(return_value=1)
    return pool


@pytest.fixture()
def mock_conn() -> AsyncMock:
    """Create a mocked asyncpg connection."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchval = AsyncMock()
    conn.execute = AsyncMock()
    conn.transaction = MagicMock()
    return conn


@pytest.fixture()
def mock_redis() -> AsyncMock:
    """Create a mocked async Redis client."""
    redis = AsyncMock()
    redis.publish = AsyncMock()
    redis.rpush = AsyncMock()
    redis.close = AsyncMock()
    return redis


@pytest.fixture()
def mock_event_emitter() -> JobsEventEmitter:
    """Create a mocked JobsEventEmitter."""
    mock_shared = AsyncMock()
    mock_shared.emit = AsyncMock(return_value="evt_test_001")
    emitter = JobsEventEmitter(mock_shared)
    return emitter


def make_job_record(
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a sample job record for tests."""
    now = datetime.now(timezone.utc)
    data: dict[str, Any] = {
        "id": 1,
        "public_id": "job_01TEST",
        "organization_id": 100,
        "title": "Senior Engineer",
        "description": "Build great things",
        "location": "San Francisco",
        "city": "San Francisco",
        "state": "CA",
        "country": "US",
        "remote_allowed": False,
        "employment_type": "full_time",
        "work_arrangement": "hybrid",
        "salary_min": 150000,
        "salary_max": 200000,
        "salary_currency": "USD",
        "show_salary": True,
        "experience_min": 5,
        "experience_max": 10,
        "education_requirement": None,
        "similar_positions_open": 1,
        "status": "draft",
        "is_public": False,
        "published_at": None,
        "closed_at": None,
        "closure_reason": None,
        "tags": [],
        "created_at": now,
        "updated_at": now,
    }
    if overrides:
        data.update(overrides)
    return data


def make_analysis_record(
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a sample job analysis record for tests."""
    now = datetime.now(timezone.utc)
    data: dict[str, Any] = {
        "id": 1,
        "public_id": "jan_01TEST",
        "job_id": 1,
        "requirement": "5 years Python experience",
        "category": "Work Experience",
        "distributed_weightage": 15.0,
        "qualification": None,
        "evidence": None,
        "mention_type": "explicit",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    if overrides:
        data.update(overrides)
    return data
