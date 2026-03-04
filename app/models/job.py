"""Pydantic schemas for job CRUD operations.

Defines request and response models for the /jobs endpoints.
Internal BIGINT ids are never exposed — only public_id.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    """Request body for creating a new job."""

    organization_public_id: str
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote_allowed: bool = False
    employment_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    show_salary: bool = False
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    education_requirement: Optional[str] = None
    similar_positions_open: int = 1
    tags: list[str] = Field(default_factory=list)


class UpdateJobRequest(BaseModel):
    """Request body for updating job fields."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote_allowed: Optional[bool] = None
    employment_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    show_salary: Optional[bool] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    education_requirement: Optional[str] = None
    similar_positions_open: Optional[int] = None
    tags: Optional[list[str]] = None


class PublishJobRequest(BaseModel):
    """Request body for publishing a job."""

    is_public: bool = False
    public_slug: Optional[str] = None


class CloseJobRequest(BaseModel):
    """Request body for closing a job."""

    closure_reason: str = Field(
        ..., description="filled, cancelled, budget, duplicate, on_hold, expired, other",
    )


class JobResponse(BaseModel):
    """Job data returned in API responses."""

    public_id: str
    organization_id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote_allowed: bool = False
    employment_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    show_salary: bool = False
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    education_requirement: Optional[str] = None
    similar_positions_open: int = 1
    status: str = "draft"
    is_public: bool = False
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
