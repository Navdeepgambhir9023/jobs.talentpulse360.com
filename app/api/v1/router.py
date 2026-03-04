"""V1 Router Aggregator.

Collects all v1 endpoint routers into a single APIRouter
that gets mounted on the FastAPI app.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.job_analysis import router as analysis_router
from app.api.v1.endpoints.job_qualifications import router as qualifications_router
from app.api.v1.endpoints.jobs import router as jobs_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(jobs_router)
v1_router.include_router(analysis_router)
v1_router.include_router(qualifications_router)
v1_router.include_router(health_router)
