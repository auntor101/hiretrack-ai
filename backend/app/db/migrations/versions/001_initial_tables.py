"""Initial tables — jobs, resumes, applications, llm_usage, user_settings, resume_scores, skill_gaps.

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("platform_job_id", sa.String(200), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("company", sa.String(200), nullable=False),
        sa.Column("location", sa.String(200), nullable=False, server_default=""),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("salary_range", sa.String(200), nullable=True),
        sa.Column("job_type", sa.String(50), nullable=True),
        sa.Column("remote", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("posted_date", sa.DateTime, nullable=True),
        sa.Column("experience_level", sa.String(50), nullable=True),
        sa.Column("match_score", sa.Float, nullable=True),
        sa.Column("skills_required", sa.JSON, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("platform", "platform_job_id", name="uq_job_platform_id"),
    )
    op.create_index("ix_job_status", "jobs", ["status"])
    op.create_index("ix_job_match_score", "jobs", ["match_score"])

    # --------------------------------------------------------------- resumes
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(20), nullable=False, server_default="base"),
        sa.Column("base_resume_id", sa.String(32), nullable=True),
        sa.Column("job_id", sa.String(32), nullable=True),
        sa.Column("template_id", sa.String(50), nullable=False, server_default="modern"),
        sa.Column("file_path_pdf", sa.String(500), nullable=True),
        sa.Column("file_path_docx", sa.String(500), nullable=True),
        sa.Column("ats_score", sa.Float, nullable=True),
        sa.Column("content_text", sa.Text, nullable=True),
        sa.Column("content_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["base_resume_id"], ["resumes.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_resume_type", "resumes", ["type"])

    # ----------------------------------------------------------- applications
    op.create_table(
        "applications",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("job_id", sa.String(32), nullable=False),
        sa.Column("resume_id", sa.String(32), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="queued"),
        sa.Column("apply_mode", sa.String(20), nullable=False, server_default="review"),
        sa.Column("ats_score", sa.Float, nullable=True),
        sa.Column("cover_letter_path", sa.String(500), nullable=True),
        sa.Column("applied_at", sa.DateTime, nullable=True),
        sa.Column("response_date", sa.DateTime, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("browser_screenshots", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_application_status", "applications", ["status"])
    op.create_index("ix_application_job_id", "applications", ["job_id"])

    # ------------------------------------------------------------ llm_usage
    op.create_table(
        "llm_usage",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("purpose", sa.String(100), nullable=False),
        sa.Column("model", sa.String(200), nullable=False, server_default=""),
        sa.Column("provider", sa.String(100), nullable=False, server_default=""),
        sa.Column("prompt_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float, nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Float, nullable=False, server_default="0"),
        sa.Column("application_id", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_llm_usage_purpose", "llm_usage", ["purpose"])

    # -------------------------------------------------------- user_settings
    op.create_table(
        "user_settings",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # -------------------------------------------------------- resume_scores
    op.create_table(
        "resume_scores",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("application_id", sa.String(32), nullable=False),
        sa.Column("overall_score", sa.Integer, nullable=False),
        sa.Column("breakdown", sa.JSON, nullable=False),
        sa.Column("scored_by", sa.String(20), nullable=False, server_default="local"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("overall_score BETWEEN 0 AND 100", name="ck_rs_score_range"),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="CASCADE"
        ),
    )

    # ---------------------------------------------------------- skill_gaps
    op.create_table(
        "skill_gaps",
        sa.Column("id", sa.String(32), primary_key=True, nullable=False),
        sa.Column("application_id", sa.String(32), nullable=False),
        sa.Column("missing_skills", sa.JSON, nullable=False),
        sa.Column("matched_skills", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="CASCADE"
        ),
    )


def downgrade() -> None:
    op.drop_table("skill_gaps")
    op.drop_table("resume_scores")
    op.drop_table("user_settings")
    op.drop_table("llm_usage")
    op.drop_index("ix_application_job_id", "applications")
    op.drop_index("ix_application_status", "applications")
    op.drop_table("applications")
    op.drop_index("ix_resume_type", "resumes")
    op.drop_table("resumes")
    op.drop_index("ix_job_match_score", "jobs")
    op.drop_index("ix_job_status", "jobs")
    op.drop_table("jobs")
