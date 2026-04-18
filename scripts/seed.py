"""Seed script — populates the database with realistic Bangladeshi tech job listings.

Run with:
    cd backend && python -m scripts.seed

Requires the database to be migrated first:
    alembic upgrade head
"""

from __future__ import annotations

import asyncio
import random
import uuid
from datetime import UTC, datetime, timedelta

from faker import Faker

fake = Faker()

# ---------------------------------------------------------------------------
# Domain data
# ---------------------------------------------------------------------------

BD_COMPANIES = [
    "Brain Station 23",
    "Shajgoj",
    "Chaldal",
    "Shohoz",
    "bKash Limited",
    "Pathao",
    "Augmedix Bangladesh",
    "Sindabad.com",
    "BJIT Group",
    "Therap (BD) Ltd.",
    "Dynamic Solution Innovators",
    "Kaz Software",
    "REVE Systems",
    "Technext Limited",
    "Reverse Resources",
    "Selise Digital Platforms",
    "SSL Wireless",
    "CrownIT",
    "Bohubrihi",
    "ShajgojTech",
]

DHAKA_LOCATIONS = [
    "Dhaka, Bangladesh (Gulshan)",
    "Dhaka, Bangladesh (Banani)",
    "Dhaka, Bangladesh (Motijheel)",
    "Dhaka, Bangladesh (Uttara)",
    "Dhaka, Bangladesh (Dhanmondi)",
    "Chattogram, Bangladesh",
    "Dhaka, Bangladesh (Remote)",
]

ROLES = [
    ("AI Engineer", ["python", "pytorch", "transformers", "llm", "mlflow"]),
    ("ML Engineer", ["python", "scikit-learn", "pandas", "tensorflow", "mlops"]),
    ("Data Analyst", ["sql", "python", "pandas", "power bi", "statistics"]),
    ("Backend Engineer", ["python", "fastapi", "postgresql", "redis", "docker"]),
    ("Python Developer", ["python", "django", "rest api", "postgresql", "git"]),
    ("LLM Engineer", ["python", "langchain", "openai", "vector databases", "rag"]),
    ("Data Engineer", ["python", "airflow", "spark", "sql", "aws"]),
    ("DevOps Engineer", ["docker", "kubernetes", "ci/cd", "terraform", "linux"]),
]

JOB_TYPES = ["full_time", "part_time", "contract"]

DESCRIPTION_TEMPLATES = [
    """We are looking for a {title} to join our engineering team at {company}.

Responsibilities:
- Design and implement scalable systems using {skill_list}
- Collaborate with cross-functional teams to deliver high-quality features
- Write clean, maintainable, and well-tested code
- Participate in code reviews and technical discussions
- Contribute to architecture decisions

Requirements:
- 2+ years of experience with {primary_skill}
- Strong understanding of software engineering principles
- Excellent problem-solving skills
- Good communication skills in English and Bengali

Nice to have:
- Experience with cloud platforms (AWS / GCP)
- Open-source contributions
- Experience in a startup environment

Location: {location}
Benefits: Competitive salary, flexible hours, health insurance, annual performance bonus.
""",
    """Join {company} as a {title} and help us build the future of tech in Bangladesh.

What you'll do:
- Build and maintain production systems with {skill_list}
- Own features end-to-end from design to deployment
- Mentor junior engineers and contribute to team growth
- Work closely with product and design teams

What we're looking for:
- Solid hands-on experience with {primary_skill}
- Ability to thrive in a fast-paced environment
- Bachelor's degree in CSE, EEE, or equivalent

Location: {location}
""",
]

STATUSES = [
    "queued", "pending_review", "applied",
    "interview", "rejected", "offer"
]
STATUS_WEIGHTS = [10, 30, 25, 15, 15, 5]


def _gen_uuid() -> str:
    return uuid.uuid4().hex


def _random_date(days_back: int = 90) -> datetime:
    return datetime.now(UTC) - timedelta(days=random.randint(0, days_back))


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

async def seed_jobs(db_session) -> list[str]:  # noqa: ANN001
    """Insert 300 job rows and return their IDs."""
    from app.models.job import Job

    job_ids: list[str] = []
    for _ in range(300):
        role, skills = random.choice(ROLES)
        company = random.choice(BD_COMPANIES)
        location = random.choice(DHAKA_LOCATIONS)
        template = random.choice(DESCRIPTION_TEMPLATES)
        description = template.format(
            title=role,
            company=company,
            location=location,
            skill_list=", ".join(skills[:3]),
            primary_skill=skills[0],
        )
        salary_min = random.randint(50, 150) * 1000
        salary_max = salary_min + random.randint(20, 80) * 1000

        job = Job(
            id=_gen_uuid(),
            platform="manual",
            platform_job_id=_gen_uuid(),
            title=role,
            company=company,
            location=location,
            url=f"https://example.com/jobs/{_gen_uuid()}",
            description=description,
            salary_range=f"BDT {salary_min:,} – {salary_max:,}",
            job_type=random.choice(JOB_TYPES),
            remote="Remote" in location,
            posted_date=_random_date(60),
            experience_level=random.choice(["junior", "mid", "senior"]),
            skills_required={"required": skills[:3], "preferred": skills[3:]},
            status="new",
        )
        db_session.add(job)
        job_ids.append(job.id)

    await db_session.flush()
    print(f"  ✓ Inserted {len(job_ids)} jobs")
    return job_ids


async def seed_applications(db_session, job_ids: list[str]) -> None:  # noqa: ANN001
    """Insert ~100 application rows linked to random jobs."""
    from app.models.application import Application

    sample_job_ids = random.sample(job_ids, min(100, len(job_ids)))
    for job_id in sample_job_ids:
        status = random.choices(STATUSES, STATUS_WEIGHTS)[0]
        applied_at = _random_date(60) if status not in ("queued", "pending_review") else None

        app = Application(
            id=_gen_uuid(),
            job_id=job_id,
            status=status,
            apply_mode="review",
            ats_score=round(random.uniform(0.3, 0.95), 2) if status != "queued" else None,
            applied_at=applied_at,
            notes=fake.sentence() if random.random() > 0.6 else None,
        )
        db_session.add(app)

    await db_session.flush()
    print(f"  ✓ Inserted {len(sample_job_ids)} applications")


async def main() -> None:
    """Entry point — runs all seed operations inside a single transaction."""
    import sys
    import os

    # Ensure the backend package is importable when run as a script
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

    from app.db.session import async_session_factory

    print("Seeding database …")
    async with async_session_factory() as db:
        job_ids = await seed_jobs(db)
        await seed_applications(db, job_ids)
        await db.commit()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
