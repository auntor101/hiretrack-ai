"""Resume scoring results model."""

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ResumeScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores ATS scoring results for a job application.

    scored_by tracks whether the score came from the local Python engine
    ('local') or from an LLM call ('llm'), so you can compare methods.
    """

    __tablename__ = "resume_scores"
    __table_args__ = (
        CheckConstraint("overall_score BETWEEN 0 AND 100", name="ck_resume_scores_range"),
    )

    application_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    breakdown: Mapped[dict] = mapped_column(JSONB, nullable=False)
    scored_by: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="local",
    )

    application: Mapped["Application"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="resume_scores",
        lazy="joined",
    )
