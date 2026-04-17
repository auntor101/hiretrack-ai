"""Job management service.

Handles job CRUD, Exa-based semantic search, and ATS job analysis.
"""

from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.config.settings import get_settings
from app.core.exceptions import RecordNotFoundError
from app.core.job_discovery.exa_search import ExaJobSearch
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.job import (
    JobAnalysisResponse,
    JobListingResponse,
    JobListResponse,
    JobSearchRequest,
)

logger = structlog.get_logger(__name__)


async def search_jobs(
    db: AsyncSession,
    request: JobSearchRequest,
) -> JobListResponse:
    """Search for jobs using Exa AI semantic search.

    Results are persisted to avoid re-fetching. Deduplication is done
    on (platform, platform_job_id). Returns empty list gracefully when
    Exa is not configured.
    """
    logger.info(
        "job_search_requested",
        query=request.query,
        location=request.location,
        limit=request.limit,
    )

    all_jobs: list[Job] = []

    try:
        settings = get_settings()
        exa_key = settings.exa_api_key.get_secret_value()
        exa = ExaJobSearch(api_key=exa_key)
        if exa.available:
            exa_listings = await exa.search_jobs(
                query=request.query,
                location=request.location,
                num_results=request.limit,
            )
            for listing in exa_listings:
                try:
                    job = _listing_from_exa(listing)
                    existing = await db.execute(
                        select(Job).where(
                            Job.platform == job.platform,
                            Job.platform_job_id == job.platform_job_id,
                        ),
                    )
                    if existing.scalar_one_or_none() is None:
                        db.add(job)
                        all_jobs.append(job)
                except Exception:
                    continue
            logger.info("job_search.exa_results", count=len(exa_listings))
    except Exception as exc:
        logger.debug("job_search.exa_skipped", reason=str(exc))

    if all_jobs:
        try:
            await db.commit()
            for job in all_jobs:
                await db.refresh(job)
        except Exception as exc:
            logger.error("job_search.commit_failed", error=str(exc))
            await db.rollback()
            all_jobs = []

    items = [JobListingResponse.model_validate(j) for j in all_jobs]
    return JobListResponse(
        items=items,
        total=len(all_jobs),
        page=1,
        page_size=request.limit,
        has_next=False,
    )


async def create_job(db: AsyncSession, data: dict[str, Any]) -> Job:
    """Manually create a job listing."""
    job = Job(
        platform=data.get("platform", "manual"),
        platform_job_id=data.get("platform_job_id", ""),
        title=data["title"],
        company=data["company"],
        location=data.get("location"),
        url=data.get("url", ""),
        description=data.get("description"),
        salary_range=data.get("salary_range"),
        job_type=data.get("job_type"),
        remote=data.get("remote", False),
        status="new",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    logger.info("job_created_manually", job_id=job.id, title=job.title)
    return job


def _listing_from_exa(listing: Any) -> Job:
    """Convert an Exa search result to a Job model."""
    salary_range: str | None = None
    if getattr(listing, "salary_min", None) is not None and getattr(listing, "salary_max", None) is not None:
        salary_range = (
            f"{listing.salary_currency} "
            f"{listing.salary_min:,.0f} - {listing.salary_max:,.0f}"
        )

    skills_dict: dict[str, Any] | None = None
    if getattr(listing, "skills_required", None) or getattr(listing, "skills_preferred", None):
        skills_dict = {
            "required": getattr(listing, "skills_required", []),
            "preferred": getattr(listing, "skills_preferred", []),
        }

    return Job(
        platform=listing.platform,
        platform_job_id=listing.platform_job_id,
        title=listing.title,
        company=listing.company,
        location=listing.location,
        url=listing.url,
        description=listing.description,
        salary_range=salary_range,
        job_type=getattr(listing, "job_type", None) or None,
        remote=getattr(listing, "remote", False),
        skills_required=skills_dict,
        status="new",
    )


async def list_jobs(
    db: AsyncSession,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    status: str | None = None,
) -> JobListResponse:
    """List jobs with pagination and optional status filter.

    Args:
        db: Async database session.
        page: Page number (1-indexed).
        page_size: Items per page.
        status: Optional status filter.

    Returns:
        Paginated job list response.
    """
    page_size = min(page_size, MAX_PAGE_SIZE)
    offset = (page - 1) * page_size

    query = select(Job)
    count_query = select(func.count(Job.id))

    if status:
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)

    query = query.order_by(Job.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    items = [JobListingResponse.model_validate(j) for j in jobs]

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


async def get_job(db: AsyncSession, job_id: str) -> Job:
    """Get a single job by ID.

    Args:
        db: Async database session.
        job_id: UUID of the job.

    Returns:
        The Job model instance.

    Raises:
        RecordNotFoundError: If job does not exist.
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise RecordNotFoundError("Job", job_id)
    return job


async def delete_job(db: AsyncSession, job_id: str) -> None:
    """Delete a job by ID.

    Args:
        db: Async database session.
        job_id: UUID of the job to delete.

    Raises:
        RecordNotFoundError: If job does not exist.
    """
    job = await get_job(db, job_id)
    await db.delete(job)
    await db.commit()
    logger.info("job_deleted", job_id=job_id)


async def analyze_job(
    db: AsyncSession,
    job_id: str,
    resume_id: str | None = None,
) -> JobAnalysisResponse:
    """Analyze job-candidate match using ATS scoring.

    If a resume_id is provided, loads the resume and runs multi-factor
    ATS scoring (skills, keywords, experience, education). Falls back to
    placeholder scores when spaCy is not available or no resume is given.

    Args:
        db: Async database session.
        job_id: UUID of the job to analyze.
        resume_id: Optional UUID of the resume to score against.

    Returns:
        Job analysis with match scores and suggestions.

    Raises:
        RecordNotFoundError: If job does not exist.
    """
    job = await get_job(db, job_id)
    logger.info("job_analysis_requested", job_id=job_id, title=job.title)

    # If no resume provided, return placeholder scores
    if not resume_id:
        return JobAnalysisResponse(
            job_id=job.id,
            match_score=0.0,
            skill_match=0.0,
            keyword_match=0.0,
            missing_skills=[],
            suggestions=[
                "Provide a resume_id to get accurate ATS scoring.",
            ],
        )

    # Load resume
    resume_result = await db.execute(
        select(Resume).where(Resume.id == resume_id),
    )
    resume = resume_result.scalar_one_or_none()
    if resume is None:
        raise RecordNotFoundError("Resume", resume_id)

    resume_text = resume.content_text or ""
    if not resume_text:
        return JobAnalysisResponse(
            job_id=job.id,
            match_score=0.0,
            skill_match=0.0,
            keyword_match=0.0,
            missing_skills=[],
            suggestions=[
                "Resume has no extracted text. Re-upload for analysis.",
            ],
        )

    # Attempt ATS scoring with spaCy
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
        from app.core.ats.experience_analyzer import ExperienceAnalyzer
        from app.core.ats.keyword_analyzer import KeywordAnalyzer
        from app.core.ats.scorer import ResumeScorer
        from app.core.ats.skill_matcher import SkillMatcher

        skill_matcher = SkillMatcher(nlp)
        keyword_analyzer = KeywordAnalyzer(nlp)
        experience_analyzer = ExperienceAnalyzer(nlp)

        scorer = ResumeScorer(
            skill_matcher=skill_matcher,
            keyword_analyzer=keyword_analyzer,
            experience_analyzer=experience_analyzer,
        )

        job_description = job.description or ""
        job_metadata: dict[str, Any] = {}
        if job.skills_required and isinstance(job.skills_required, dict):
            job_metadata["required_skills"] = job.skills_required.get(
                "required", job.skills_required.get("skills", []),
            )
            job_metadata["preferred_skills"] = job.skills_required.get(
                "preferred", [],
            )

        # Extract skills from resume text for candidate profile
        detected_skills = list(skill_matcher.extract_skills(resume_text))
        candidate_profile: dict[str, Any] = {
            "skills": detected_skills,
            "experience": [],
            "education": [],
        }

        details = scorer.score_resume(
            resume_text=resume_text,
            job_description=job_description,
            candidate_profile=candidate_profile,
            job_metadata=job_metadata,
        )

        return JobAnalysisResponse(
            job_id=job.id,
            match_score=details.overall_score,
            skill_match=details.skill_score,
            keyword_match=details.keyword_score,
            missing_skills=details.missing_required_skills,
            suggestions=details.improvement_suggestions,
        )

    except (ImportError, OSError) as exc:
        logger.warning(
            "job_analysis.spacy_unavailable",
            error=str(exc),
        )
        return JobAnalysisResponse(
            job_id=job.id,
            match_score=0.0,
            skill_match=0.0,
            keyword_match=0.0,
            missing_skills=[],
            suggestions=[
                "spaCy NLP model not available. Install with: "
                "python -m spacy download en_core_web_sm",
            ],
        )
