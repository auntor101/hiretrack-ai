"""Pydantic schemas for job-related API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobCreate(BaseModel):
    """Request body for manually adding a job listing."""

    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=2000)
    location: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=50_000)
    job_type: str | None = Field(default=None, pattern="^(full_time|part_time|contract|internship)$")
    remote: bool = False
    salary_range: str | None = Field(default=None, max_length=100)
    experience_level: str | None = Field(default=None, pattern="^(junior|mid|senior|lead|executive)$")
    skills_required: dict[str, Any] | None = None
    platform: str = Field(default="manual", max_length=50)
    platform_job_id: str = Field(default="", max_length=200)

    @field_validator("platform_job_id", mode="before")
    @classmethod
    def _default_platform_job_id(cls, v: str | None, info: Any) -> str:
        """Auto-generate a platform_job_id from the URL if not provided."""
        if not v:
            import hashlib  # noqa: PLC0415
            url = info.data.get("url", "")
            return hashlib.sha1(url.encode()).hexdigest()[:16]  # noqa: S324
        return v


class JobSearchRequest(BaseModel):
    """Request body for multi-platform job search."""

    query: str = Field(..., min_length=1, max_length=500)
    location: str = ""
    platforms: list[str] = Field(default_factory=lambda: ["linkedin", "indeed", "glassdoor"])
    filters: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=20, ge=1, le=100)


class JobListingResponse(BaseModel):
    """Single job listing in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    platform: str
    platform_job_id: str
    title: str
    company: str
    location: str
    url: str
    description: str
    salary_range: str | None = None
    job_type: str | None = None
    remote: bool = False
    posted_date: datetime | None = None
    experience_level: str | None = None
    match_score: float | None = None
    skills_required: dict | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    """Paginated list of job listings."""

    items: list[JobListingResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class JobAnalysisResponse(BaseModel):
    """Response for job analysis endpoint."""

    job_id: str
    match_score: float
    skill_match: float
    keyword_match: float
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
