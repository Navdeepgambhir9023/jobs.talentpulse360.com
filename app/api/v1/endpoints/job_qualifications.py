"""Job qualifications endpoint.

Handles HTTP concerns for job qualification criteria.
Route prefix: /v1/jobs/{job_public_id}/qualifications
"""

from fastapi import APIRouter, Depends
from tp360_shared.models.responses import DataResponse

from app.api.deps import get_job_qualification_service
from app.models.job_qualification import (
    JobQualificationResponse,
    UpsertJobQualificationRequest,
)
from app.services.job_qualification_service import JobQualificationService

router = APIRouter(
    prefix="/jobs/{job_public_id}/qualifications",
    tags=["job-qualifications"],
)


@router.get(
    "",
    response_model=DataResponse,
    summary="Get job qualification criteria",
)
async def get_qualifications(
    job_public_id: str,
    service: JobQualificationService = Depends(get_job_qualification_service),
) -> DataResponse:
    """Get qualification criteria for a job.

    Args:
        job_public_id: Job ULID public identifier.
        service: Injected JobQualificationService.

    Returns:
        DataResponse wrapping qualification record.
    """
    record = await service.get_qualifications(job_public_id)
    if record is None:
        return DataResponse(data={})
    return DataResponse(data=JobQualificationResponse(**record).model_dump())


@router.put(
    "",
    response_model=DataResponse,
    summary="Create or update job qualification criteria",
)
async def upsert_qualifications(
    job_public_id: str,
    body: UpsertJobQualificationRequest,
    service: JobQualificationService = Depends(get_job_qualification_service),
) -> DataResponse:
    """Create or update qualification criteria for a job.

    Args:
        job_public_id: Job ULID public identifier.
        body: Validated qualification data.
        service: Injected JobQualificationService.

    Returns:
        DataResponse wrapping the qualification record.
    """
    record = await service.upsert_qualifications(
        job_public_id, body.model_dump(),
    )
    return DataResponse(data=JobQualificationResponse(**record).model_dump())
