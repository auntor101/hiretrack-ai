"""HireTrack AI — Streamlit home / nav page.
Drop-in replacement: uses ht_components for branded visuals.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import requests
import streamlit as st
from utils import API_BASE, api_get, _auth_headers, cold_start_guard
from ht_components import (
    inject_global_css, dark_hero, section_header,
    kpi_row, info_box, job_card_html,
    HT_COLORS,
)

st.set_page_config(
    page_title="HireTrack AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()
cold_start_guard()

# ── Data ──────────────────────────────────────────────────────────────────────
stats = api_get("/dashboard/stats") or {}
jobs  = api_get("/jobs/", params={"page": 1, "page_size": 6}) or {}

# ── Hero ──────────────────────────────────────────────────────────────────────
hero_stats = [
    {"value": stats.get("total_applications", 0), "label": "Applications"},
    {"value": stats.get("by_status", {}).get("interview", 0), "label": "Interviews"},
    {"value": stats.get("by_status", {}).get("offer", 0), "label": "Offers"},
    {"value": f"{stats.get('avg_ats_score', 0):.0%}", "label": "Avg ATS Score"},
]
dark_hero(
    title="Your Job Search Command Center",
    gradient_word="Command Center",
    subtitle=(
        "Discover roles, score your ATS compatibility, generate tailored cover letters, "
        "and track every application — all from one place."
    ),
    stats=hero_stats,
)

# ── Feature highlights ────────────────────────────────────────────────────────
kpi_row([
    {"value": "AI Matching",      "label": "LLM-based resume scoring against every JD",         "icon": "✦", "color": HT_COLORS["blue_500"]},
    {"value": "ATS Optimizer",    "label": "Know your score before you apply",                   "icon": "📈", "color": HT_COLORS["violet_500"]},
    {"value": "Cover Letters",    "label": "Tailored letters generated in seconds",              "icon": "✉️", "color": HT_COLORS["success"]},
    {"value": "Full Pipeline",    "label": "Queued → Applied → Interview → Offer tracking",     "icon": "🎯", "color": HT_COLORS["warning"]},
])

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ── Latest opportunities ──────────────────────────────────────────────────────
section_header("Latest Opportunities")
items = (jobs.get("items") or [])[:6]

if not items:
    info_box("No jobs found yet. Use the Job Board to search or add listings.")
else:
    cols = st.columns(2)
    for i, job in enumerate(items):
        match = job.get("match_score") or job.get("ats_score")
        if match and match <= 1.0:
            match = int(match * 100)
        with cols[i % 2]:
            st.markdown(job_card_html(job, match_score=match), unsafe_allow_html=True)
