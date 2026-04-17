"""Dashboard API routes.

Provides a single aggregated stats endpoint used by the Streamlit frontend
and any external clients that need a summary of the application pipeline.
"""

from collections import Counter

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.application import Application
from app.models.skill_gap import SkillGap
from app.schemas.application import DashboardStats

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Aggregated pipeline statistics",
)
async def get_stats(db: AsyncSession = Depends(get_db)) -> DashboardStats:
    """Return top-level dashboard statistics.

    Counts applications by status, computes the average ATS score across all
    scored applications, and surfaces the most frequently missing skills from
    stored skill-gap analyses.
    """
    total_result = await db.execute(select(func.count(Application.id)))
    total = total_result.scalar() or 0

    status_result = await db.execute(
        select(Application.status, func.count(Application.id)).group_by(Application.status)
    )
    by_status: dict[str, int] = {row[0]: row[1] for row in status_result.all()}

    avg_result = await db.execute(
        select(func.avg(Application.ats_score)).where(Application.ats_score.isnot(None))
    )
    avg_ats = round(float(avg_result.scalar() or 0.0), 1)

    gaps_result = await db.execute(select(SkillGap.missing_skills))
    all_missing: list[str] = []
    for row in gaps_result.scalars().all():
        if isinstance(row, list):
            all_missing.extend(row)

    counter = Counter(all_missing)
    top_missing = [
        {"skill": skill, "count": count}
        for skill, count in counter.most_common(10)
    ]

    logger.info("dashboard_stats_fetched", total=total, avg_ats=avg_ats)
    return DashboardStats(
        total_applications=total,
        by_status=by_status,
        top_missing_skills=top_missing,
        avg_ats_score=avg_ats,
    )
