"""Applications tracker page."""
from __future__ import annotations

import html
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import (
    API_BASE,
    STATUS_COLORS,
    api_get,
    api_post,
    api_put,
    ats_badge_html,
    inject_global_css,
    status_badge_html,
)

st.set_page_config(
    page_title="Applications \u00b7 AutoApply AI",
    page_icon="\U0001f4ca",
    layout="wide",
)
inject_global_css()

st.markdown(
    '<div class="page-title">\U0001f4ca Application Tracker</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-subtitle">Track every application through your pipeline</div>',
    unsafe_allow_html=True,
)

# ── Status KPIs ───────────────────────────────────────────────────────────────
dash = api_get("/dashboard/stats") or {}
by_status: dict = dash.get("by_status", {})

cols = st.columns(6)
status_kpis = [
    ("pending_review", "\U0001f50d Pending", "#F59E0B"),
    ("applied", "\U0001f4e8 Applied", "#06B6D4"),
    ("interview", "\U0001f3af Interview", "#10B981"),
    ("offer", "\U0001f389 Offer", "#22C55E"),
    ("rejected", "\u274c Rejected", "#EF4444"),
    ("queued", "\u23f3 Queued", "#6B7280"),
]
for col, (key, label, color) in zip(cols, status_kpis):
    col.markdown(
        f"""<div class="kpi-card" style="border-top-color:{color}">
            <div class="kpi-value" style="font-size:28px">{by_status.get(key, 0)}</div>
            <div class="kpi-label">{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters + Export ──────────────────────────────────────────────────────────
filter_col, export_col = st.columns([5, 1])
STATUS_OPTIONS = [
    "All", "Queued", "Pending Review", "Applied",
    "Interview", "Offer", "Rejected", "Withdrawn",
]
STATUS_KEYS = {
    "All": None, "Queued": "queued", "Pending Review": "pending_review",
    "Applied": "applied", "Interview": "interview", "Offer": "offer",
    "Rejected": "rejected", "Withdrawn": "withdrawn",
}
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
        '<button style="background:#0A66C2;color:white;border:none;border-radius:8px;'
        'padding:8px 16px;cursor:pointer;font-weight:600;font-size:13px;width:100%">'
        "\u2b07\ufe0f Export CSV</button></a>",
        unsafe_allow_html=True,
    )

selected_status = STATUS_KEYS[sel_tab]
params: dict = {"page": 1, "page_size": 100}
if selected_status:
    params["status"] = selected_status

data = api_get("/applications/", params=params) or {}
items: list[dict] = data.get("items", [])
total = data.get("total", 0)

# ── Build job lookup map ───────────────────────────────────────────────────────
jobs_data = api_get("/jobs/", params={"page_size": 200}) or {}
job_map: dict[str, dict] = {j["id"]: j for j in jobs_data.get("items", [])}

st.markdown(
    f'<div style="font-size:13px;color:#6B7280;margin-bottom:12px">'
    f"{total} application(s) found</div>",
    unsafe_allow_html=True,
)

# ── Application cards ─────────────────────────────────────────────────────────
if not items:
    st.markdown(
        '<div class="info-box">No applications found for this filter.</div>',
        unsafe_allow_html=True,
    )
else:
    for app in items:
        job = job_map.get(app.get("job_id", ""), {})
        job_title = html.escape(job.get("title", "Unknown Position"))
        company = html.escape(job.get("company", "Unknown Company"))
        status = app.get("status", "queued")
        border_color = STATUS_COLORS.get(status, "#E5E7EB")

        applied_at = app.get("applied_at")
        date_str = ""
        if applied_at:
            try:
                dt = datetime.fromisoformat(applied_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%b %d, %Y")
            except Exception:
                date_str = str(applied_at)[:10]

        notes_html = (
            f'<div style="font-size:13px;color:#6B7280;margin-top:6px;font-style:italic">'
            f'\U0001f4dd {html.escape(str(app["notes"]))}</div>'
            if app.get("notes")
            else ""
        )

        st.markdown(
            f"""
            <div class="app-card" style="border-left-color:{border_color}">
                <div style="display:flex;justify-content:space-between;
                            align-items:flex-start;flex-wrap:wrap;gap:8px">
                    <div>
                        <div class="app-card-title">{job_title}</div>
                        <div class="app-card-company">\U0001f3e2 {company}</div>
                    </div>
                    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
                        {status_badge_html(status)}
                        {ats_badge_html(app.get("ats_score"))}
                        {f'<span style="font-size:12px;color:#9CA3AF">\U0001f4c5 {date_str}</span>' if date_str else ''}
                    </div>
                </div>
                {notes_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Manage application"):
            left, right = st.columns(2)

            with left:
                st.markdown("**Update Status**")
                valid_statuses = [
                    "queued", "pending_review", "approved", "applied",
                    "interview", "offer", "rejected", "withdrawn",
                ]
                current_idx = valid_statuses.index(status) if status in valid_statuses else 0
                new_status = st.selectbox(
                    "Status",
                    valid_statuses,
                    index=current_idx,
                    key=f"sel_status_{app['id']}",
                    label_visibility="collapsed",
                )
                notes = st.text_area(
                    "Notes",
                    value=app.get("notes") or "",
                    key=f"notes_{app['id']}",
                    height=68,
                )
                if st.button("Save", key=f"upd_{app['id']}", type="primary"):
                    res = api_put(
                        f"/applications/{app['id']}/status",
                        {"status": new_status, "notes": notes or None},
                    )
                    if res:
                        st.success("Updated!")
                        st.rerun()

            with right:
                st.markdown("**AI Actions**")
                a1, a2, a3 = st.columns(3)

                with a1:
                    if st.button("\U0001f3af Score", key=f"score_{app['id']}"):
                        with st.spinner("Scoring..."):
                            res = api_post(f"/applications/{app['id']}/score-resume")
                        if res:
                            score = res.get("overall_score", 0)
                            st.markdown(f"**Overall: {score}/100**")
                            for k, v in (res.get("breakdown") or {}).items():
                                if isinstance(v, (int, float)):
                                    # st.progress expects 0.0–1.0; API returns 0–100 percent
                                    st.progress(float(v) / 100, text=f"{k.title()}: {v:.0f}%")

                with a2:
                    if st.button("\U0001f50d Gap", key=f"gap_{app['id']}"):
                        with st.spinner("Analysing..."):
                            res = api_post(f"/applications/{app['id']}/skill-gap")
                        if res:
                            matched = res.get("matched_skills", [])
                            missing = res.get("missing_skills", [])
                            st.markdown(
                                f"**Matched:** {', '.join(matched[:5]) or 'None'}"
                            )
                            st.markdown(
                                f"**Missing:** {', '.join(missing[:5]) or 'None'}"
                            )

                with a3:
                    if st.button("\u2709\ufe0f Letter", key=f"cl_{app['id']}"):
                        with st.spinner("Generating..."):
                            res = api_post(f"/applications/{app['id']}/cover-letter")
                        if res:
                            st.text_area(
                                "Cover Letter",
                                value=res.get("text", ""),
                                height=200,
                                key=f"cl_text_{app['id']}",
                            )
