"""Dependency Injection for jobs-service.

Provides FastAPI Depends() callables that construct repository,
service, and event emitter instances from the shared connection pool.
"""

import asyncpg
from fastapi import Request

from app.events.emitter import JobsEventEmitter
from app.repositories.category_weightage_repo import CategoryWeightageRepository
from app.repositories.job_analysis_repo import JobAnalysisRepository
from app.repositories.job_qualification_repo import JobQualificationRepository
from app.repositories.job_repo import JobRepository
from app.repositories.job_weightage_repo import JobWeightageRepository
from app.services.job_analysis_service import JobAnalysisService
from app.services.job_qualification_service import JobQualificationService
from app.services.job_service import JobService


async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Return the shared database connection pool."""
    return request.app.state.db_pool


async def get_event_emitter(request: Request) -> JobsEventEmitter:
    """Return the domain event emitter."""
    return request.app.state.event_emitter


# --- Repository factories ---

async def get_job_repo(request: Request) -> JobRepository:
    """Create a JobRepository instance."""
    return JobRepository(request.app.state.db_pool)


async def get_analysis_repo(request: Request) -> JobAnalysisRepository:
    """Create a JobAnalysisRepository instance."""
    return JobAnalysisRepository(request.app.state.db_pool)


async def get_weightage_repo(request: Request) -> JobWeightageRepository:
    """Create a JobWeightageRepository instance."""
    return JobWeightageRepository(request.app.state.db_pool)


async def get_category_repo(request: Request) -> CategoryWeightageRepository:
    """Create a CategoryWeightageRepository instance."""
    return CategoryWeightageRepository(request.app.state.db_pool)


async def get_qualification_repo(request: Request) -> JobQualificationRepository:
    """Create a JobQualificationRepository instance."""
    return JobQualificationRepository(request.app.state.db_pool)


# --- Service factories ---

async def get_job_service(request: Request) -> JobService:
    """Create a JobService instance with dependencies."""
    pool = request.app.state.db_pool
    return JobService(
        JobRepository(pool),
        request.app.state.event_emitter,
    )


async def get_job_analysis_service(request: Request) -> JobAnalysisService:
    """Create a JobAnalysisService instance with dependencies."""
    pool = request.app.state.db_pool
    return JobAnalysisService(
        JobRepository(pool),
        JobAnalysisRepository(pool),
        request.app.state.event_emitter,
    )


async def get_job_qualification_service(
    request: Request,
) -> JobQualificationService:
    """Create a JobQualificationService instance with dependencies."""
    pool = request.app.state.db_pool
    return JobQualificationService(
        JobRepository(pool),
        JobQualificationRepository(pool),
        request.app.state.event_emitter,
    )
