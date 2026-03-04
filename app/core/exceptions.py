"""Jobs-service-specific exceptions.

Extends the tp360_shared exception hierarchy with domain-specific errors.
These exceptions are raised by the service layer, never by endpoints.
"""

from tp360_shared.errors.exceptions import AppError


class JobNotFoundError(AppError):
    """Raised when a job is not found."""

    def __init__(self, public_id: str) -> None:
        super().__init__(
            code="JOB_NOT_FOUND",
            message=f"Job '{public_id}' not found",
            status_code=404,
        )


class InvalidJobStatusTransitionError(AppError):
    """Raised when a job status transition is invalid."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            code="INVALID_JOB_STATUS_TRANSITION",
            message=f"Cannot transition job from '{current}' to '{target}'",
            status_code=409,
        )


class JobAlreadyPublishedError(AppError):
    """Raised when trying to publish an already-published job."""

    def __init__(self, public_id: str) -> None:
        super().__init__(
            code="JOB_ALREADY_PUBLISHED",
            message=f"Job '{public_id}' is already published",
            status_code=409,
        )


class JobRequirementLimitError(AppError):
    """Raised when requirement count exceeds limit."""

    def __init__(self, job_public_id: str, limit: int) -> None:
        super().__init__(
            code="JOB_REQUIREMENT_LIMIT",
            message=f"Job '{job_public_id}' exceeds {limit} requirements",
            status_code=400,
        )
