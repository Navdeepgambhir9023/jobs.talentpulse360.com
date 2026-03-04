"""Tests for app.models — Pydantic request/response schemas."""

import pytest
from pydantic import ValidationError

from app.models.job import (
    CloseJobRequest,
    CreateJobRequest,
    JobResponse,
    PublishJobRequest,
    UpdateJobRequest,
)
from app.models.job_analysis import (
    CreateJobAnalysisRequest,
    JobAnalysisResponse,
)
from app.models.job_qualification import (
    JobQualificationResponse,
    UpsertJobQualificationRequest,
)
from tests.conftest import make_analysis_record, make_job_record


class TestCreateJobRequest:
    """Tests for CreateJobRequest validation."""

    def test_valid_request(self):
        req = CreateJobRequest(
            organization_public_id="org_01TEST",
            title="Senior Engineer",
        )
        assert req.title == "Senior Engineer"

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            CreateJobRequest(organization_public_id="org_01", title="")

    def test_defaults(self):
        req = CreateJobRequest(
            organization_public_id="org_01",
            title="Test",
        )
        assert req.remote_allowed is False
        assert req.salary_currency == "USD"
        assert req.similar_positions_open == 1
        assert req.tags == []


class TestUpdateJobRequest:
    """Tests for UpdateJobRequest validation."""

    def test_all_optional(self):
        req = UpdateJobRequest()
        assert req.title is None
        assert req.salary_min is None

    def test_partial_update(self):
        req = UpdateJobRequest(title="Updated Title")
        dump = req.model_dump(exclude_unset=True)
        assert dump == {"title": "Updated Title"}


class TestPublishJobRequest:
    """Tests for PublishJobRequest."""

    def test_default_not_public(self):
        req = PublishJobRequest()
        assert req.is_public is False
        assert req.public_slug is None


class TestCloseJobRequest:
    """Tests for CloseJobRequest."""

    def test_requires_reason(self):
        with pytest.raises(ValidationError):
            CloseJobRequest()

    def test_valid_reason(self):
        req = CloseJobRequest(closure_reason="filled")
        assert req.closure_reason == "filled"


class TestJobResponse:
    """Tests for JobResponse serialization."""

    def test_from_record(self):
        record = make_job_record()
        resp = JobResponse(**record)
        assert resp.public_id == "job_01TEST"
        assert resp.status == "draft"


class TestCreateJobAnalysisRequest:
    """Tests for analysis request validation."""

    def test_valid_request(self):
        req = CreateJobAnalysisRequest(
            requirement="5 years Python",
            category="Work Experience",
        )
        assert req.requirement == "5 years Python"

    def test_empty_requirement_raises(self):
        with pytest.raises(ValidationError):
            CreateJobAnalysisRequest(requirement="", category="Work Experience")


class TestJobAnalysisResponse:
    """Tests for analysis response serialization."""

    def test_from_record(self):
        record = make_analysis_record()
        resp = JobAnalysisResponse(**record)
        assert resp.public_id == "jan_01TEST"


class TestUpsertJobQualificationRequest:
    """Tests for qualification request validation."""

    def test_defaults(self):
        req = UpsertJobQualificationRequest()
        assert req.qualification_threshold == 50.0
        assert req.auto_qualification_enabled is False
        assert req.salary_currency == "USD"

    def test_custom_values(self):
        req = UpsertJobQualificationRequest(
            country="US",
            visa_sponsorship=True,
            qualification_threshold=75.0,
        )
        assert req.country == "US"
        assert req.visa_sponsorship is True
