"""Skill gap analysis results model."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SkillGap(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores skill gap analysis for a job application.

    missing_skills: skills in the job description not found in the resume.
    matched_skills: skills present in both resume and job description.
    """

    __tablename__ = "skill_gaps"

    application_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    missing_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    matched_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    application: Mapped["Application"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="skill_gaps",
        lazy="joined",
    )
