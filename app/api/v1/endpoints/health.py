"""Health endpoint.

Route prefix: /health
"""

from fastapi import APIRouter, Depends
from tp360_shared.db.health_check import check_database_health
from tp360_shared.models.responses import DataResponse

from app.api.deps import get_db_pool
from app.models.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=DataResponse,
    summary="Health check",
)
async def health_check(
    pool=Depends(get_db_pool),
) -> DataResponse:
    """Check service and database health.

    Args:
        pool: Injected asyncpg connection pool.

    Returns:
        DataResponse wrapping health status.
    """
    is_db_healthy = await check_database_health(pool)
    status_value = "healthy" if is_db_healthy else "degraded"
    return DataResponse(
        data=HealthResponse(
            status=status_value,
            service="jobs-service",
            is_database_connected=is_db_healthy,
        ).model_dump(),
    )
