"""Background worker that polls the database for queued applications.

Replaces the Redis-based queue with a lightweight DB-polling approach.
Uses SELECT FOR UPDATE SKIP LOCKED so the worker is safe to run in-process
alongside the FastAPI app without double-processing any application.

Pipeline per application:
  queued → applying (locked) → ATS score → generate resume → pending_review
  (or failed on any fatal error)
"""

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select

from app.api.websocket.events import manager as ws_manager
from app.config.constants import ApplicationStatus
from app.config.settings import get_settings
from app.core.exceptions import AutoApplyError
from app.db.session import async_session_factory
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.resume import ResumeGenerateRequest
from app.services import resume as resume_service

logger = structlog.get_logger(__name__)

# How long to sleep between polls when no work is found (seconds)
_POLL_INTERVAL = 5


async def _broadcast_progress(
    application_id: str,
    status: str,
    detail: str = "",
) -> None:
    """Send application progress update via WebSocket."""
    message: dict[str, Any] = {
        "type": "application_progress",
        "application_id": application_id,
        "status": status,
    }
    if detail:
        message["detail"] = detail
    await ws_manager.broadcast(message)


async def _update_application_status(
    app_id: str,
    status: str,
    notes: str | None = None,
    ats_score: float | None = None,
    applied_at: datetime | None = None,
) -> None:
    """Persist application status changes to the database."""
    try:
        async with async_session_factory() as db:
            result = await db.execute(
                select(Application).where(Application.id == app_id),
            )
            app = result.scalar_one_or_none()
            if app is None:
                logger.warning("worker.app_not_found_for_update", app_id=app_id)
                return
            app.status = status
            if notes is not None:
                app.notes = notes
            if ats_score is not None:
                app.ats_score = ats_score
            if applied_at is not None:
                app.applied_at = applied_at
            await db.commit()
    except Exception as exc:
        logger.error(
            "worker.status_update_failed",
            app_id=app_id,
            error=str(exc),
        )


async def _run_ats_scoring(job: Job, resume_id: str) -> float | None:
    """Run ATS scoring for a job against a resume.

    Returns the overall score or None if scoring cannot be performed.
    """
    if not resume_id:
        return None

    try:
        async with async_session_factory() as db:
            result = await db.execute(
                select(Resume).where(Resume.id == resume_id),
            )
            resume = result.scalar_one_or_none()

        if resume is None or not resume.content_text:
            logger.warning("worker.ats_no_resume_text", resume_id=resume_id)
            return None

        from app.core.ats.experience_analyzer import ExperienceAnalyzer
        from app.core.ats.scorer import ResumeScorer

        try:
            import spacy

            nlp = spacy.load("en_core_web_sm")
            from app.core.ats.keyword_analyzer import KeywordAnalyzer
            from app.core.ats.skill_matcher import SkillMatcher

            skill_matcher = SkillMatcher(nlp)
            keyword_analyzer = KeywordAnalyzer(nlp)
            experience_analyzer = ExperienceAnalyzer(nlp)
        except (ImportError, OSError):
            logger.warning("worker.spacy_unavailable_for_ats")
            return None

        scorer = ResumeScorer(
            skill_matcher=skill_matcher,
            keyword_analyzer=keyword_analyzer,
            experience_analyzer=experience_analyzer,
        )

        job_description = job.description or ""
        job_metadata: dict[str, Any] = {}
        if job.skills_required and isinstance(job.skills_required, dict):
            job_metadata["required_skills"] = job.skills_required.get("required", [])

        candidate_profile: dict[str, Any] = {
            "skills": [],
            "experience": [],
            "education": [],
        }

        score_details = scorer.score_resume(
            resume_text=resume.content_text,
            job_description=job_description,
            candidate_profile=candidate_profile,
            job_metadata=job_metadata,
        )
        return score_details.overall_score

    except Exception as exc:
        logger.warning("worker.ats_scoring_error", error=str(exc))
        return None


async def process_application(payload: dict[str, Any]) -> None:
    """Process a single application payload.

    Pipeline: load job → ATS score resume → generate tailored resume.
    Applications are then set to pending_review for human approval.
    """
    job_id: str = payload.get("job_id", "")
    app_id: str = payload.get("application_id", "")
    resume_id: str = payload.get("resume_id", "")

    logger.info("worker.processing", job_id=job_id, app_id=app_id)
    await _broadcast_progress(app_id, "processing")

    try:
        settings = get_settings()
        min_score = settings.min_ats_score

        # Step 1: Load job
        await _broadcast_progress(app_id, "loading_job")
        job: Job | None = None
        try:
            async with async_session_factory() as db:
                result = await db.execute(select(Job).where(Job.id == job_id))
                job = result.scalar_one_or_none()
        except Exception as exc:
            logger.error("worker.load_job_failed", job_id=job_id, error=str(exc))

        if job is None:
            error_msg = f"Job {job_id} not found"
            await _update_application_status(app_id, ApplicationStatus.FAILED, notes=error_msg)
            await _broadcast_progress(app_id, ApplicationStatus.FAILED, detail=error_msg)
            return

        # Step 2: ATS score
        await _broadcast_progress(app_id, "scoring_ats")
        ats_score: float | None = None
        try:
            ats_score = await _run_ats_scoring(job, resume_id)
            logger.info("worker.ats_scored", app_id=app_id, score=ats_score)
        except Exception as exc:
            logger.warning("worker.ats_scoring_failed", app_id=app_id, error=str(exc))

        if ats_score is not None and ats_score < min_score:
            skip_msg = f"ATS score {ats_score:.2f} below threshold {min_score:.2f}"
            await _update_application_status(
                app_id, ApplicationStatus.FAILED, notes=skip_msg, ats_score=ats_score,
            )
            await _broadcast_progress(app_id, ApplicationStatus.FAILED, detail=skip_msg)
            return

        # Step 3: Generate tailored resume (best-effort)
        await _broadcast_progress(app_id, "generating_resume")
        try:
            if resume_id:
                async with async_session_factory() as db:
                    gen_request = ResumeGenerateRequest(
                        base_resume_id=resume_id,
                        job_id=job_id,
                        template_id="modern",
                    )
                    tailored_resp = await resume_service.generate_tailored_resume(db, gen_request)
                    logger.info("worker.resume_generated", resume_id=tailored_resp.id)
        except Exception as exc:
            logger.warning("worker.resume_generation_failed", app_id=app_id, error=str(exc))

        # Done — ready for manual review
        await _update_application_status(
            app_id,
            ApplicationStatus.PENDING_REVIEW,
            ats_score=ats_score,
        )
        await _broadcast_progress(app_id, ApplicationStatus.PENDING_REVIEW)
        logger.info("worker.completed", job_id=job_id, app_id=app_id)

    except AutoApplyError as exc:
        logger.error(
            "worker.application_error",
            job_id=job_id, app_id=app_id, error=str(exc), code=exc.code,
        )
        await _update_application_status(app_id, ApplicationStatus.FAILED, notes=str(exc))
        await _broadcast_progress(app_id, ApplicationStatus.FAILED, detail=str(exc))

    except Exception as exc:
        logger.error("worker.unexpected_error", job_id=job_id, app_id=app_id, error=str(exc))
        await _update_application_status(
            app_id, ApplicationStatus.FAILED, notes=f"Unexpected error: {exc}",
        )
        await _broadcast_progress(app_id, ApplicationStatus.FAILED, detail="Unexpected error")


async def _pick_and_lock_queued() -> dict[str, Any] | None:
    """Atomically claim one queued application and set it to APPLYING.

    Uses SELECT FOR UPDATE SKIP LOCKED so concurrent workers (or restarts)
    never double-process the same application.

    Returns a payload dict or None if nothing is queued.
    """
    async with async_session_factory() as db:
        result = await db.execute(
            select(Application)
            .where(Application.status == ApplicationStatus.QUEUED)
            .order_by(Application.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True),
        )
        application = result.scalar_one_or_none()

        if application is None:
            return None

        # Claim it immediately so no other worker picks it up
        application.status = ApplicationStatus.APPLYING
        await db.commit()

        return {
            "application_id": application.id,
            "job_id": application.job_id,
            "resume_id": application.resume_id or "",
        }


async def run_worker() -> None:
    """Main worker loop — polls the database for queued applications.

    Runs forever as an asyncio background task alongside the FastAPI server.
    Polls every {_POLL_INTERVAL} seconds when idle; processes immediately
    when work is found. Handles cancellation gracefully on shutdown.
    """
    logger.info("worker.started", mode="db_poll", poll_interval=_POLL_INTERVAL)

    while True:
        try:
            payload = await _pick_and_lock_queued()
            if payload is not None:
                await process_application(payload)
            else:
                await asyncio.sleep(_POLL_INTERVAL)
        except asyncio.CancelledError:
            logger.info("worker.stopped")
            return
        except Exception as exc:
            logger.error("worker.loop_error", error=str(exc))
            await asyncio.sleep(_POLL_INTERVAL)
