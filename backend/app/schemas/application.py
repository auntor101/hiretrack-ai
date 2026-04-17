"""Pydantic schemas for application-related API requests and responses."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApplyModeEnum(StrEnum):
    """Valid apply modes for application creation."""

    AUTONOMOUS = "autonomous"
    REVIEW = "review"
    BATCH = "batch"


class StatusEnum(StrEnum):
    """Valid application status values."""

    QUEUED = "queued"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    APPLYING = "applying"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class ApplicationCreate(BaseModel):
    """Request to create a single job application."""

    job_id: str
    resume_id: str | None = None
    apply_mode: ApplyModeEnum = ApplyModeEnum.REVIEW


class ApplicationBatchCreate(BaseModel):
    """Request to create multiple job applications at once."""

    job_ids: list[str] = Field(..., min_length=1)
    resume_id: str | None = None
    apply_mode: ApplyModeEnum = ApplyModeEnum.REVIEW


class ApplicationStatusUpdate(BaseModel):
    """Request to update application status."""

    status: StatusEnum
    notes: str | None = None


class ApplicationResponse(BaseModel):
    """Single application in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    resume_id: str | None = None
    status: str
    apply_mode: str
    ats_score: float | None = None
    cover_letter_path: str | None = None
    applied_at: datetime | None = None
    response_date: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""

    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int


class ResumeScoreOut(BaseModel):
    """Resume ATS score result."""

    model_config = ConfigDict(from_attributes=True)

    overall_score: int
    breakdown: dict
    scored_by: str


class SkillGapOut(BaseModel):
    """Skill gap analysis result."""

    model_config = ConfigDict(from_attributes=True)

    missing_skills: list[str]
    matched_skills: list[str]


class CoverLetterOut(BaseModel):
    """Generated cover letter text."""

    text: str
    template_used: str


class DashboardStats(BaseModel):
    """High-level pipeline statistics for the dashboard."""

    total_applications: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    top_missing_skills: list[dict[str, Any]] = Field(default_factory=list)
    avg_ats_score: float = 0.0
