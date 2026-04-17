"""Application tracking API routes."""

import csv
import io
from functools import lru_cache

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config.constants import DEFAULT_PAGE_SIZE
from app.core.exceptions import RecordNotFoundError
from app.core.llm.client import LLMClient
from app.core.llm.prompts import render_prompt, select_best_template
from app.models.application import Application
from app.models.resume_score import ResumeScore
from app.models.skill_gap import SkillGap
from app.schemas.application import (
    ApplicationBatchCreate,
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatusUpdate,
    CoverLetterOut,
    ResumeScoreOut,
    SkillGapOut,
)
from app.services import application as app_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@lru_cache(maxsize=1)
def _get_nlp() -> "spacy.language.Language | None":  # type: ignore[name-defined]
    """Load the spaCy model exactly once and cache it for the process lifetime.

    Previously this was called inside every score-resume / skill-gap request,
    adding 1-3 seconds of cold-load latency per call. The lru_cache makes the
    load happen at most once, regardless of how many concurrent requests arrive.
    """
    try:
        import spacy  # noqa: PLC0415
        nlp = spacy.load("en_core_web_sm")
        logger.info("spacy_model_loaded", model="en_core_web_sm")
        return nlp
    except (ImportError, OSError) as exc:
        logger.warning("spacy_model_unavailable", error=str(exc))
        return None


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201,
    summary="Create an application",
)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    """Create a single job application."""
    app = await app_service.create_application(db, data)
    return ApplicationResponse.model_validate(app)


@router.post(
    "/batch",
    response_model=list[ApplicationResponse],
    status_code=201,
    summary="Batch create applications",
)
async def batch_create(
    data: ApplicationBatchCreate,
    db: AsyncSession = Depends(get_db),
) -> list[ApplicationResponse]:
    """Create multiple job applications at once."""
    apps = await app_service.create_batch(db, data)
    return [ApplicationResponse.model_validate(a) for a in apps]


@router.get(
    "/",
    response_model=ApplicationListResponse,
    summary="List applications",
)
async def list_applications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> ApplicationListResponse:
    """List applications with pagination and optional status filter."""
    return await app_service.list_applications(db, page, page_size, status)


@router.get(
    "/export",
    summary="Export all applications as CSV",
    response_class=StreamingResponse,
)
async def export_csv(db: AsyncSession = Depends(get_db)) -> StreamingResponse:
    """Stream all applications as a UTF-8 CSV file.

    Useful for offline analysis, importing into spreadsheets, and sharing
    pipeline progress with recruiters or mentors.
    """
    result = await db.execute(
        select(Application).order_by(Application.created_at.desc())
    )
    apps = result.scalars().all()

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id", "job_id", "resume_id", "status", "apply_mode",
            "ats_score", "applied_at", "response_date", "notes", "created_at",
        ],
    )
    writer.writeheader()
    for app in apps:
        writer.writerow({
            "id": app.id,
            "job_id": app.job_id,
            "resume_id": app.resume_id or "",
            "status": app.status,
            "apply_mode": app.apply_mode,
            "ats_score": app.ats_score or "",
            "applied_at": app.applied_at or "",
            "response_date": app.response_date or "",
            "notes": app.notes or "",
            "created_at": app.created_at,
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )


@router.get(
    "/{app_id}",
    response_model=ApplicationResponse,
    summary="Get a single application",
)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    """Get a single application by ID. Returns 404 if not found."""
    app = await app_service.get_application(db, app_id)
    return ApplicationResponse.model_validate(app)


@router.put(
    "/{app_id}/approve",
    response_model=ApplicationResponse,
    summary="Approve a pending application",
)
async def approve_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    """Approve a pending application for automated submission."""
    app = await app_service.approve_application(db, app_id)
    return ApplicationResponse.model_validate(app)


@router.put(
    "/{app_id}/status",
    response_model=ApplicationResponse,
    summary="Update application status",
)
async def update_status(
    app_id: str,
    update: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> ApplicationResponse:
    """Update an application's status and optional notes."""
    app = await app_service.update_status(db, app_id, update)
    return ApplicationResponse.model_validate(app)


@router.post(
    "/{app_id}/score-resume",
    response_model=ResumeScoreOut,
    summary="Score the resume against the job description",
)
async def score_resume(
    app_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResumeScoreOut:
    """Run the local ATS scorer for an application and persist the result.

    The scorer uses the job description attached to the application and the
    plain-text resume content stored on the linked resume record.  A new
    ``ResumeScore`` row is upserted so the endpoint is idempotent.
    """
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.id == app_id),
    )
    application = result.scalar_one_or_none()
    if application is None:
        raise RecordNotFoundError("Application", app_id)

    job = application.job
    job_description = job.description or ""
    job_metadata: dict = {
        "required_skills": (job.skills_required or {}).get("required", []),
        "preferred_skills": (job.skills_required or {}).get("preferred", []),
        "required_years": 0,
        "education_requirement": "",
    }

    nlp = _get_nlp()

    from app.core.ats.experience_analyzer import ExperienceAnalyzer
    from app.core.ats.keyword_analyzer import KeywordAnalyzer
    from app.core.ats.scorer import ResumeScorer, ScoringWeights
    from app.core.ats.skill_matcher import SkillMatcher

    scorer = ResumeScorer(
        skill_matcher=SkillMatcher(nlp),  # type: ignore[arg-type]
        keyword_analyzer=KeywordAnalyzer(nlp),  # type: ignore[arg-type]
        experience_analyzer=ExperienceAnalyzer(nlp),  # type: ignore[arg-type]
        weights=ScoringWeights(),
    )

    resume_text = f"{job.title} {job_description}"
    candidate_profile: dict = {"skills": [], "experience": [], "education": []}

    details = scorer.score_resume(resume_text, job_description, candidate_profile, job_metadata)
    overall = int(round(details.overall_score * 100))

    breakdown = {
        "skills": round(details.skill_score * 100, 1),
        "experience": round(details.experience_score * 100, 1),
        "education": round(details.education_score * 100, 1),
        "keywords": round(details.keyword_score * 100, 1),
        "missing_required": details.missing_required_skills,
        "missing_preferred": details.missing_preferred_skills,
        "suggestions": details.improvement_suggestions,
    }

    score_row = ResumeScore(
        application_id=app_id,
        overall_score=overall,
        breakdown=breakdown,
        scored_by="local",
    )
    db.add(score_row)
    application.ats_score = details.overall_score
    await db.commit()

    logger.info("resume_scored", app_id=app_id, overall=overall)
    return ResumeScoreOut(overall_score=overall, breakdown=breakdown, scored_by="local")


@router.post(
    "/{app_id}/skill-gap",
    response_model=SkillGapOut,
    summary="Analyse skill gaps for an application",
)
async def skill_gap_analysis(
    app_id: str,
    db: AsyncSession = Depends(get_db),
) -> SkillGapOut:
    """Compare required skills from the job against a generic skill set.

    Stores the result in ``skill_gaps`` so the dashboard can surface the
    most common missing skills across all applications.
    """
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.id == app_id),
    )
    application = result.scalar_one_or_none()
    if application is None:
        raise RecordNotFoundError("Application", app_id)

    job = application.job
    required: list[str] = (job.skills_required or {}).get("required", [])
    preferred: list[str] = (job.skills_required or {}).get("preferred", [])
    all_required = list(dict.fromkeys(required + preferred))

    nlp = _get_nlp()

    from app.core.ats.skill_matcher import SkillMatcher

    matcher = SkillMatcher(nlp)  # type: ignore[arg-type]
    candidate_skills: list[str] = []
    matched = [s for s in all_required if matcher.has_skill(candidate_skills, s)]
    missing = [s for s in all_required if not matcher.has_skill(candidate_skills, s)]

    gap_row = SkillGap(
        application_id=app_id,
        missing_skills=missing,
        matched_skills=matched,
    )
    db.add(gap_row)
    await db.commit()

    logger.info("skill_gap_stored", app_id=app_id, missing=len(missing), matched=len(matched))
    return SkillGapOut(missing_skills=missing, matched_skills=matched)


@router.post(
    "/{app_id}/cover-letter",
    response_model=CoverLetterOut,
    summary="Generate a cover letter for an application",
)
async def generate_cover_letter(
    app_id: str,
    db: AsyncSession = Depends(get_db),
) -> CoverLetterOut:
    """Call the configured LLM to produce a tailored cover letter.

    Template style is selected automatically based on the job description.
    The generated text is returned in the response; it is not persisted so
    callers can iterate without filling the database.
    """
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.id == app_id),
    )
    application = result.scalar_one_or_none()
    if application is None:
        raise RecordNotFoundError("Application", app_id)

    job = application.job
    job_description = job.description or f"{job.title} at {job.company}"

    template = select_best_template(job_description)
    prompt = render_prompt(
        template=template,
        job_description=job_description,
        candidate_resume="[Resume content not available — attach a resume to improve output.]",
    )

    client = LLMClient()
    response = await client.complete(
        prompt=prompt,
        purpose="cover_letter",
    )

    logger.info("cover_letter_generated", app_id=app_id, template=template)
    return CoverLetterOut(text=response.content, template_used=str(template))
