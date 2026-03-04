"""Pydantic schemas for job analysis operations.

Defines request and response models for /jobs/{id}/analysis endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobAnalysisResponse(BaseModel):
    """Single job analysis requirement row."""

    public_id: str
    requirement: str
    category: str
    distributed_weightage: Optional[float] = None
    qualification: Optional[str] = None
    evidence: Optional[str] = None
    mention_type: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class CreateJobAnalysisRequest(BaseModel):
    """Request body for adding an analysis requirement."""

    requirement: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    distributed_weightage: Optional[float] = None
    qualification: Optional[str] = None
    evidence: Optional[str] = None
    mention_type: Optional[str] = None
