"""Pydantic schemas for job qualifications.

Defines request and response models for /jobs/{id}/qualifications endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobQualificationResponse(BaseModel):
    """Job qualification criteria returned in API responses."""

    public_id: str
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    location_flexibility: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "USD"
    employment_types: list[str] = Field(default_factory=list)
    work_arrangements: list[str] = Field(default_factory=list)
    travel_required: bool = False
    visa_sponsorship: bool = False
    timezone: Optional[str] = None
    qualification_threshold: float = 50.0
    auto_qualification_enabled: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UpsertJobQualificationRequest(BaseModel):
    """Request body for creating/updating job qualifications."""

    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    location_flexibility: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "USD"
    employment_types: list[str] = Field(default_factory=list)
    work_arrangements: list[str] = Field(default_factory=list)
    travel_required: bool = False
    visa_sponsorship: bool = False
    timezone: Optional[str] = None
    qualification_threshold: float = 50.0
    auto_qualification_enabled: bool = False
