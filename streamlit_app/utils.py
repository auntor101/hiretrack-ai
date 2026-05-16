"""Shared utilities for the AutoApply AI Streamlit dashboard."""
from __future__ import annotations

import html
import os
from typing import Any

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def _auth_headers() -> dict[str, str]:
    key = st.secrets.get("API_SECRET_KEY", "") or os.getenv("API_SECRET_KEY", "")
    return {"X-API-Key": key} if key else {}

STATUS_COLORS: dict[str, str] = {
    "queued": "#6B7280",
    "pending_review": "#F59E0B",
    "approved": "#3B82F6",
    "applying": "#8B5CF6",
    "applied": "#06B6D4",
    "interview": "#10B981",
    "offer": "#22C55E",
    "rejected": "#EF4444",
    "withdrawn": "#9CA3AF",
    "failed": "#DC2626",
    "new": "#6B7280",
}

STATUS_EMOJI: dict[str, str] = {
    "queued": "\u23f3",
    "pending_review": "\U0001f50d",
    "approved": "\u2705",
    "applying": "\U0001f4dd",
    "applied": "\U0001f4e8",
    "interview": "\U0001f3af",
    "offer": "\U0001f389",
    "rejected": "\u274c",
    "withdrawn": "\u21a9\ufe0f",
    "failed": "\u26a0\ufe0f",
    "new": "\U0001f195",
}

EXP_COLORS: dict[str, str] = {
    "junior": "#10B981",
    "mid": "#3B82F6",
    "senior": "#8B5CF6",
}

JOB_TYPE_LABELS: dict[str, str] = {
    "full_time": "Full-time",
    "part_time": "Part-time",
    "contract": "Contract",
    "internship": "Internship",
}


def _backend_warning(kind: str) -> None:
    if kind == "timeout":
        st.warning(
            "⏳ **Backend is warming up** — Render free tier sleeps after inactivity. "
            "Wait 30 seconds then **reload the page**.",
            icon="🔄",
        )
    elif kind == "conn":
        st.warning(
            "🔴 **Cannot reach the backend.** "
            f"Check that `API_BASE_URL` is set correctly in Streamlit secrets. "
            f"Current value: `{API_BASE}`",
            icon="⚠️",
        )
    if not st.session_state.get("_warn_btn_shown"):
        st.session_state["_warn_btn_shown"] = True
        if st.button("🔄 Retry Connection", key="retry_backend_conn"):
            for k in ("_warn_btn_shown", "_backend_ok", "_warmup_n"):
                st.session_state.pop(k, None)
            st.rerun()


def cold_start_guard() -> None:
    """Poll /health until Render wakes up, showing a countdown banner.
    Sets session_state['_backend_ok'] so subsequent pages skip the wait.
    """
    import time as _t

    if st.session_state.get("_backend_ok"):
        return

    health = API_BASE.rstrip("/api/v1").rstrip("/") + "/health"
    try:
        r = requests.get(health, headers=_auth_headers(), timeout=8)
        if r.status_code < 500:
            st.session_state["_backend_ok"] = True
            st.session_state.pop("_warmup_n", None)
            return
    except Exception:
        pass

    n = st.session_state.get("_warmup_n", 0)
    if n >= 12:
        st.session_state.pop("_warmup_n", None)
        st.error(
            "⚠️ **Backend not responding** after 2 minutes. "
            "Check `API_BASE_URL` in Streamlit secrets, then reload."
        )
        st.stop()

    st.session_state["_warmup_n"] = n + 1
    remaining = (12 - n) * 10
    st.info(
        f"⏳ **Backend warming up...** ({remaining}s remaining)  \n"
        "Render free tier sleeps after inactivity — first load takes **30–60 seconds**."
    )
    _t.sleep(10)
    st.rerun()


def api_get(path: str, params: dict | None = None) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.get(url, params=params, headers=_auth_headers(), timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        _backend_warning("timeout")
        return None
    except requests.exceptions.ConnectionError:
        _backend_warning("conn")
        return None
    except requests.exceptions.HTTPError as e:
        st.warning(f"API error {e.response.status_code}: {e.response.text[:200]}")
        return None


def api_post(path: str, json: dict | None = None) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.post(url, json=json or {}, headers=_auth_headers(), timeout=90)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        _backend_warning("timeout")
        return None
    except requests.exceptions.ConnectionError:
        _backend_warning("conn")
        return None
    except requests.exceptions.HTTPError as e:
        st.warning(f"API error: {e.response.text[:200]}")
        return None


def api_upload(path: str, file_bytes: bytes, filename: str, content_type: str) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.post(
            url,
            files={"file": (filename, file_bytes, content_type)},
            headers=_auth_headers(),
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        _backend_warning("timeout")
        return None
    except requests.exceptions.ConnectionError:
        _backend_warning("conn")
        return None
    except requests.exceptions.HTTPError as e:
        st.warning(f"Upload error: {e.response.text[:200]}")
        return None


def api_put(path: str, json: dict | None = None) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.put(url, json=json or {}, headers=_auth_headers(), timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        _backend_warning("timeout")
        return None
    except requests.exceptions.ConnectionError:
        _backend_warning("conn")
        return None
    except requests.exceptions.HTTPError as e:
        st.warning(f"API error: {e.response.text[:200]}")
        return None


def status_badge_html(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6B7280")
    emoji = STATUS_EMOJI.get(status, "\u2022")
    label = html.escape(status.replace("_", " ").title())
    return (
        f'<span style="background:{color};color:white;padding:3px 12px;'
        f'border-radius:12px;font-size:12px;font-weight:600;white-space:nowrap">'
        f"{emoji} {label}</span>"
    )


def ats_badge_html(score: float | None) -> str:
    if score is None:
        return '<span style="color:#9CA3AF;font-size:13px;font-weight:500">N/A</span>'
    pct = int(score * 100)
    if pct >= 80:
        color = "#22C55E"
    elif pct >= 60:
        color = "#F59E0B"
    else:
        color = "#EF4444"
    # pct is an integer derived from a float — safe, no escaping needed
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:8px;font-size:13px;font-weight:700">{pct}%</span>'
    )


def exp_badge_html(level: str | None) -> str:
    if not level:
        return ""
    color = EXP_COLORS.get(level, "#6B7280")
    safe_level = html.escape(level)
    return (
        f'<span style="background:{color}20;color:{color};padding:2px 8px;'
        f'border-radius:6px;font-size:11px;font-weight:600;text-transform:uppercase">'
        f"{safe_level}</span>"
    )


def skill_tags_html(skills: list[str]) -> str:
    tags = "".join(
        f'<span style="background:#EFF6FF;color:#1D4ED8;border-radius:6px;'
        f'padding:2px 10px;font-size:12px;font-weight:500;margin:2px;display:inline-block">'
        f"{html.escape(s)}</span>"
        for s in skills[:6]
    )
    return tags


