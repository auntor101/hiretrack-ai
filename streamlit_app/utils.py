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


def api_get(path: str, params: dict | None = None) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.get(url, params=params, headers=_auth_headers(), timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "\U0001f534 Cannot connect to the backend. "
            "Make sure FastAPI is running on port 8000."
        )
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text[:200]}")
        return None


def api_post(path: str, json: dict | None = None) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.post(url, json=json or {}, headers=_auth_headers(), timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("\U0001f534 Cannot connect to the backend.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.text[:200]}")
        return None


def api_put(path: str, json: dict | None = None) -> Any:
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        r = requests.put(url, json=json or {}, headers=_auth_headers(), timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("\U0001f534 Cannot connect to the backend.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.text[:200]}")
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


