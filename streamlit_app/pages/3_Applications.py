"""Applications tracker — full pipeline with AI actions.
Drop-in replacement: uses ht_components for branded visuals.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import API_BASE, api_get, api_post, api_put
from ht_components import (
    inject_global_css, page_header, section_header,
    app_card_html, kpi_row, status_chip_html, ats_chip_html,
    ai_callout, info_box, skill_tags_html,
    HT_COLORS, HT_STATUS,
)

st.set_page_config(
    page_title="Applications · HireTrack AI",
    page_icon="📊",
    layout="wide",
)
inject_global_css()
page_header("My Applications", "Track every application through your pipeline.")

# ── Status KPIs ───────────────────────────────────────────────────────────────
dash      = api_get("/dashboard/stats") or {}
by_status = dash.get("by_status", {})

kpi_row([
    {"value": by_status.get("pending_review", 0), "label": "Pending Review", "icon": "🔍", "color": HT_COLORS["warning"]},
    {"value": by_status.get("applied", 0),        "label": "Applied",        "icon": "📨", "color": HT_COLORS["blue_500"]},
    {"value": by_status.get("interview", 0),      "label": "Interview",      "icon": "🎯", "color": HT_COLORS["violet_500"]},
    {"value": by_status.get("offer", 0),           "label": "Offer",          "icon": "⭐", "color": HT_COLORS["success"]},
    {"value": by_status.get("rejected", 0),       "label": "Rejected",       "icon": "✕",  "color": HT_COLORS["error"]},
    {"value": by_status.get("queued", 0),          "label": "Queued",         "icon": "⏳", "color": HT_COLORS["ink_muted"]},
])

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ── Filters + Export ──────────────────────────────────────────────────────────
STATUS_OPTIONS = [
    "All", "Queued", "Pending Review", "Applied",
    "Interview", "Offer", "Rejected", "Withdrawn",
]
STATUS_KEYS = {
    "All": None,
    "Queued": "queued",
    "Pending Review": "pending_review",
    "Applied": "applied",
    "Interview": "interview",
    "Offer": "offer",
    "Rejected": "rejected",
    "Withdrawn": "withdrawn",
}

filter_col, export_col = st.columns([5, 1])
with filter_col:
    sel_tab = st.radio(
        "Filter",
        STATUS_OPTIONS,
        horizontal=True,
        label_visibility="collapsed",
    )
with export_col:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<a href="{API_BASE}/applications/export" target="_blank">'
        '<button style="background:linear-gradient(135deg,#0A66C2,#1570E0);color:white;'
        'border:none;border-radius:10px;padding:8px 16px;cursor:pointer;font-weight:600;'
        'font-size:13px;width:100%;font-family:inherit">↓ Export CSV</button></a>',
        unsafe_allow_html=True,
    )

selected_status = STATUS_KEYS[sel_tab]
params: dict = {"page": 1, "page_size": 100}
if selected_status:
    params["status"] = selected_status

data  = api_get("/applications/", params=params) or {}
items = data.get("items", [])
total = data.get("total", 0)

# Job lookup map
jobs_data = api_get("/jobs/", params={"page_size": 200}) or {}
job_map   = {j["id"]: j for j in jobs_data.get("items", [])}

st.markdown(
    f'<div style="font-size:13px;color:#64748B;margin:4px 0 12px">'
    f'{total} application(s) found</div>',
    unsafe_allow_html=True,
)

# ── Application cards ─────────────────────────────────────────────────────────
if not items:
    info_box("No applications found for this filter.")
else:
    for app in items:
        job = job_map.get(app.get("job_id", ""), {})

        # Date string
        applied_at = app.get("applied_at")
        date_str   = ""
        if applied_at:
            try:
                dt       = datetime.fromisoformat(applied_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%b %d, %Y")
            except Exception:
                date_str = str(applied_at)[:10]

        st.markdown(app_card_html(app, job), unsafe_allow_html=True)

        with st.expander("Manage application"):
            left, right = st.columns(2)

            with left:
                section_header("Update Status")
                valid_statuses = [
                    "queued", "pending_review", "approved", "applied",
                    "interview", "offer", "rejected", "withdrawn",
                ]
                current_idx = valid_statuses.index(app.get("status", "queued")) \
                    if app.get("status") in valid_statuses else 0
                new_status = st.selectbox(
                    "Status",
                    valid_statuses,
                    format_func=lambda s: HT_STATUS.get(s, {}).get("label", s.replace("_", " ").title()),
                    index=current_idx,
                    key=f"sel_status_{app['id']}",
                    label_visibility="collapsed",
                )
                notes = st.text_area(
                    "Notes",
                    value=app.get("notes") or "",
                    key=f"notes_{app['id']}",
                    height=68,
                    placeholder="Add notes about this application…",
                )
                if st.button("Save", key=f"upd_{app['id']}", type="primary"):
                    res = api_put(
                        f"/applications/{app['id']}/status",
                        {"status": new_status, "notes": notes or None},
                    )
                    if res:
                        info_box("Updated successfully.", kind="success")
                        st.rerun()

            with right:
                section_header("AI Actions")
                a1, a2, a3 = st.columns(3)

                with a1:
                    if st.button("🎯 Score Resume", key=f"score_{app['id']}"):
                        with st.spinner("Scoring…"):
                            res = api_post(f"/applications/{app['id']}/score-resume")
                        if res:
                            score = res.get("overall_score", 0)
                            st.markdown(f"**Overall: {score}/100**")
                            for k, v in (res.get("breakdown") or {}).items():
                                if isinstance(v, (int, float)):
                                    st.progress(float(v) / 100, text=f"{k.title()}: {v:.0f}%")

                with a2:
                    if st.button("🔍 Skill Gap", key=f"gap_{app['id']}"):
                        with st.spinner("Analysing…"):
                            res = api_post(f"/applications/{app['id']}/skill-gap")
                        if res:
                            have    = res.get("matched_skills", [])
                            missing = res.get("missing_skills", [])
                            st.markdown(
                                skill_tags_html(
                                    have + missing,
                                    have=have,
                                    missing=missing,
                                ),
                                unsafe_allow_html=True,
                            )

                with a3:
                    if st.button("✉️ Cover Letter", key=f"cl_{app['id']}"):
                        with st.spinner("Generating…"):
                            res = api_post(f"/applications/{app['id']}/cover-letter")
                        if res:
                            ai_callout(res.get("text", ""), title="Generated Cover Letter")
