"""Unit tests for the application worker (app.workers.application_worker).

All external dependencies (DB, Redis, WebSocket manager) are mocked so
these tests run without infrastructure.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from app.config.constants import ApplicationStatus
from app.workers.application_worker import process_application

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_payload(
    job_id: str = "job-1",
    application_id: str = "app-1",
    resume_id: str = "",
) -> dict:
    return {
        "job_id": job_id,
        "application_id": application_id,
        "resume_id": resume_id,
    }


def _make_mock_job():
    """Create a mock Job model instance."""
    job = MagicMock()
    job.id = "job-1"
    job.title = "Senior Python Dev"
    job.company = "TestCorp"
    job.location = "Remote"
    job.url = "https://example.com/job/123"
    job.description = "We need a Python developer"
    job.job_type = "full-time"
    job.remote = True
    job.skills_required = {"required": ["python"], "preferred": ["fastapi"]}
    return job


def _make_mock_session(job=None):
    """Create an async context manager mock for async_session_factory."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = job
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    return mock_session


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestProcessApplicationHappyPath:
    async def test_process_application_reaches_pending_review(self):
        """Worker should set PENDING_REVIEW when job is found."""
        payload = _make_payload()
        mock_job = _make_mock_job()

        with (
            patch("app.workers.application_worker.ws_manager") as mock_ws,
            patch("app.workers.application_worker.get_settings") as mock_settings,
            patch("app.workers.application_worker.async_session_factory") as mock_sf,
            patch(
                "app.workers.application_worker._update_application_status",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            mock_ws.broadcast = AsyncMock()
            mock_settings.return_value = MagicMock(min_ats_score=0.75)

            mock_session = _make_mock_session(mock_job)
            mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_sf.return_value.__aexit__ = AsyncMock(return_value=False)

            await process_application(payload)

        statuses_updated = [call.args[1] for call in mock_update.call_args_list]
        # Final status should be PENDING_REVIEW (not APPLIED — no browser submission)
        assert ApplicationStatus.PENDING_REVIEW in statuses_updated

    async def test_process_application_broadcasts_loading_job(self):
        """Worker should broadcast loading_job at start."""
        payload = _make_payload()

        with (
            patch("app.workers.application_worker.ws_manager") as mock_ws,
            patch("app.workers.application_worker.get_settings") as mock_settings,
            patch("app.workers.application_worker.async_session_factory") as mock_sf,
            patch("app.workers.application_worker._update_application_status", new_callable=AsyncMock),
        ):
            mock_ws.broadcast = AsyncMock()
            mock_settings.return_value = MagicMock(min_ats_score=0.75)

            mock_session = _make_mock_session(_make_mock_job())
            mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_sf.return_value.__aexit__ = AsyncMock(return_value=False)

            await process_application(payload)

        statuses = [call.args[0]["status"] for call in mock_ws.broadcast.call_args_list]
        assert "loading_job" in statuses

    async def test_process_application_sets_application_id(self):
        """Every broadcast should include the application_id."""
        payload = _make_payload(application_id="app-42")

        with (
            patch("app.workers.application_worker.ws_manager") as mock_ws,
            patch("app.workers.application_worker.get_settings") as mock_settings,
            patch("app.workers.application_worker.async_session_factory") as mock_sf,
            patch("app.workers.application_worker._update_application_status", new_callable=AsyncMock),
        ):
            mock_ws.broadcast = AsyncMock()
            mock_settings.return_value = MagicMock(min_ats_score=0.75)

            mock_session = _make_mock_session(_make_mock_job())
            mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_sf.return_value.__aexit__ = AsyncMock(return_value=False)

            await process_application(payload)

        for call in mock_ws.broadcast.call_args_list:
            assert call.args[0]["application_id"] == "app-42"


class TestProcessApplicationErrors:
    async def test_worker_handles_job_not_found(self):
        """When the job is not found in DB, worker should broadcast FAILED."""
        payload = _make_payload()

        with (
            patch("app.workers.application_worker.ws_manager") as mock_ws,
            patch("app.workers.application_worker.get_settings") as mock_settings,
            patch("app.workers.application_worker.async_session_factory") as mock_sf,
            patch("app.workers.application_worker._update_application_status", new_callable=AsyncMock),
        ):
            mock_ws.broadcast = AsyncMock()
            mock_settings.return_value = MagicMock(min_ats_score=0.75)

            mock_session = _make_mock_session(None)
            mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_sf.return_value.__aexit__ = AsyncMock(return_value=False)

            await process_application(payload)

        last_call = mock_ws.broadcast.call_args_list[-1]
        msg = last_call.args[0]
        assert msg["status"] == ApplicationStatus.FAILED
        assert "not found" in msg.get("detail", "").lower()

    async def test_worker_handles_empty_payload(self):
        """Worker should handle missing keys without crashing."""
        payload: dict = {}

        with (
            patch("app.workers.application_worker.ws_manager") as mock_ws,
            patch("app.workers.application_worker._update_application_status", new_callable=AsyncMock),
        ):
            mock_ws.broadcast = AsyncMock()
            await process_application(payload)

        assert mock_ws.broadcast.call_count >= 1

    async def test_worker_fails_below_ats_threshold(self):
        """When ATS score is below min_ats_score, application should fail."""
        payload = _make_payload(resume_id="resume-1")
        mock_job = _make_mock_job()

        with (
            patch("app.workers.application_worker.ws_manager") as mock_ws,
            patch("app.workers.application_worker.get_settings") as mock_settings,
            patch("app.workers.application_worker.async_session_factory") as mock_sf,
            patch("app.workers.application_worker._run_ats_scoring", new_callable=AsyncMock, return_value=0.1),
            patch("app.workers.application_worker._update_application_status", new_callable=AsyncMock) as mock_update,
        ):
            mock_ws.broadcast = AsyncMock()
            mock_settings.return_value = MagicMock(min_ats_score=0.75)

            mock_session = _make_mock_session(mock_job)
            mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_sf.return_value.__aexit__ = AsyncMock(return_value=False)

            await process_application(payload)

        statuses_updated = [call.args[1] for call in mock_update.call_args_list]
        assert ApplicationStatus.FAILED in statuses_updated


class TestBroadcastProgress:
    async def test_broadcast_includes_detail_when_provided(self):
        """_broadcast_progress should include detail in the message."""
        from app.workers.application_worker import _broadcast_progress

        with patch("app.workers.application_worker.ws_manager") as mock_ws:
            mock_ws.broadcast = AsyncMock()
            await _broadcast_progress("app-1", "applying", detail="Step 1")

        msg = mock_ws.broadcast.call_args.args[0]
        assert msg["detail"] == "Step 1"

    async def test_broadcast_omits_detail_when_empty(self):
        """_broadcast_progress should not include detail key when not provided."""
        from app.workers.application_worker import _broadcast_progress

        with patch("app.workers.application_worker.ws_manager") as mock_ws:
            mock_ws.broadcast = AsyncMock()
            await _broadcast_progress("app-1", "applying")

        msg = mock_ws.broadcast.call_args.args[0]
        assert "detail" not in msg
