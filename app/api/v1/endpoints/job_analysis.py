"""Job analysis endpoint.

Handles HTTP concerns for job analysis requirement operations.
Route prefix: /v1/jobs/{job_public_id}/analysis
"""

from fastapi import APIRouter, Depends, status
from tp360_shared.models.responses import DataResponse, ListResponse

from app.api.deps import get_job_analysis_service
from app.models.job_analysis import (
    CreateJobAnalysisRequest,
    JobAnalysisResponse,
)
from app.services.job_analysis_service import JobAnalysisService

router = APIRouter(prefix="/jobs/{job_public_id}/analysis", tags=["job-analysis"])


@router.get(
    "",
    response_model=ListResponse,
    summary="Get job analysis requirements",
)
async def get_analysis(
    job_public_id: str,
    service: JobAnalysisService = Depends(get_job_analysis_service),
) -> ListResponse:
    """Get all analysis requirements for a job.

    Args:
        job_public_id: Job ULID public identifier.
        service: Injected JobAnalysisService.

    Returns:
        ListResponse wrapping analysis records.
    """
    records = await service.get_analysis(job_public_id)
    data = [JobAnalysisResponse(**r).model_dump() for r in records]
    return ListResponse(data=data)


@router.post(
    "",
    response_model=DataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add analysis requirement",
)
async def add_requirement(
    job_public_id: str,
    body: CreateJobAnalysisRequest,
    service: JobAnalysisService = Depends(get_job_analysis_service),
) -> DataResponse:
    """Add a requirement to a job's analysis.

    Args:
        job_public_id: Job ULID public identifier.
        body: Validated requirement data.
        service: Injected JobAnalysisService.

    Returns:
        DataResponse wrapping the created requirement.
    """
    record = await service.add_requirement(
        job_public_id, body.model_dump(),
    )
    return DataResponse(data=JobAnalysisResponse(**record).model_dump())
