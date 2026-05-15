"""Shared FastAPI dependencies for route injection."""

from collections.abc import AsyncGenerator

from fastapi import Header, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.db.redis import get_redis as _get_redis
from app.db.session import get_db as _get_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async for session in _get_db():
        yield session


def get_redis() -> Redis | None:
    """Redis client dependency. Returns None if Redis unavailable."""
    return _get_redis()


async def verify_api_key(x_api_key: str = Header(default="")) -> None:
    """Enforce X-API-Key header for personal-use auth.

    If API_SECRET_KEY is not configured the check is skipped (development mode).
    In production, every request to protected routes must include the header.
    """
    secret = get_settings().api_secret_key
    if secret and x_api_key != secret:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")
