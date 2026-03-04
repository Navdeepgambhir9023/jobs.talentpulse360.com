"""Jobs endpoint.

Handles HTTP concerns for job CRUD and lifecycle operations.
Route prefix: /v1/jobs
"""

from fastapi import APIRouter, Depends, status
from tp360_shared.models.responses import DataResponse, ListResponse

from app.api.deps import get_job_service
from app.models.job import (
    CloseJobRequest,
    CreateJobRequest,
    JobResponse,
    PublishJobRequest,
    UpdateJobRequest,
)
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=DataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
)
async def create_job(
    body: CreateJobRequest,
    service: JobService = Depends(get_job_service),
) -> DataResponse:
    """Create a new job posting in draft status.

    Args:
        body: Validated job creation payload.
        service: Injected JobService.

    Returns:
        DataResponse wrapping the created job.
    """
    job = await service.create_job(body.model_dump())
    return DataResponse(data=JobResponse(**job).model_dump())


@router.get(
    "/{public_id}",
    response_model=DataResponse,
    summary="Get job by public_id",
)
async def get_job(
    public_id: str,
    service: JobService = Depends(get_job_service),
) -> DataResponse:
    """Get a single job.

    Args:
        public_id: Job ULID public identifier.
        service: Injected JobService.

    Returns:
        DataResponse wrapping the job.
    """
    job = await service.get_job(public_id)
    return DataResponse(data=JobResponse(**job).model_dump())


@router.patch(
    "/{public_id}",
    response_model=DataResponse,
    summary="Update job fields",
)
async def update_job(
    public_id: str,
    body: UpdateJobRequest,
    service: JobService = Depends(get_job_service),
) -> DataResponse:
    """Partially update job fields.

    Args:
        public_id: Job ULID public identifier.
        body: Fields to update.
        service: Injected JobService.

    Returns:
        DataResponse wrapping the updated job.
    """
    updated = await service.update_job(
        public_id, body.model_dump(exclude_unset=True),
    )
    return DataResponse(data=JobResponse(**updated).model_dump())


@router.post(
    "/{public_id}/publish",
    response_model=DataResponse,
    summary="Publish a job",
)
async def publish_job(
    public_id: str,
    body: PublishJobRequest,
    service: JobService = Depends(get_job_service),
) -> DataResponse:
    """Publish a job (transition to published status).

    Args:
        public_id: Job ULID public identifier.
        body: Publication options.
        service: Injected JobService.

    Returns:
        DataResponse wrapping the published job.
    """
    job = await service.publish_job(
        public_id, body.is_public, body.public_slug,
    )
    return DataResponse(data=JobResponse(**job).model_dump())


@router.post(
    "/{public_id}/close",
    response_model=DataResponse,
    summary="Close a job",
)
async def close_job(
    public_id: str,
    body: CloseJobRequest,
    service: JobService = Depends(get_job_service),
) -> DataResponse:
    """Close a job with a reason.

    Args:
        public_id: Job ULID public identifier.
        body: Closure details.
        service: Injected JobService.

    Returns:
        DataResponse wrapping the closed job.
    """
    job = await service.close_job(public_id, body.closure_reason)
    return DataResponse(data=JobResponse(**job).model_dump())


@router.post(
    "/{public_id}/request-analysis",
    response_model=DataResponse,
    summary="Request AI analysis for a job",
)
async def request_analysis(
    public_id: str,
    service: JobService = Depends(get_job_service),
) -> DataResponse:
    """Request AI analysis of the job description.

    Args:
        public_id: Job ULID public identifier.
        service: Injected JobService.

    Returns:
        DataResponse wrapping the job.
    """
    job = await service.request_analysis(public_id)
    return DataResponse(data=JobResponse(**job).model_dump())
