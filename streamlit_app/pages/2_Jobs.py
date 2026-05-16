"""Job listings page — browse, filter, and apply to jobs.
Drop-in replacement: uses ht_components for branded visuals.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import JOB_TYPE_LABELS, api_get, api_post
from ht_components import (
    inject_global_css, page_header, section_header,
    job_card_html, info_box, kpi_row, HT_COLORS,
)

st.set_page_config(
    page_title="Job Board · HireTrack AI",
    page_icon="💼",
    layout="wide",
)
inject_global_css()
page_header("Job Board", "Browse and apply to curated opportunities.")

# ── Filters ───────────────────────────────────────────────────────────────────
fc1, fc2, fc3, fc4, fc5 = st.columns([3, 1, 1, 1, 1])
with fc1:
    search_q = st.text_input(
        "",
        placeholder="🔍  Search by title, company, or skill…",
        label_visibility="collapsed",
    )
with fc2:
    remote_opt = st.selectbox(
        "Location",
        ["All", "Remote Only", "On-site Only"],
        label_visibility="collapsed",
    )
with fc3:
    jtype_opt = st.selectbox(
        "Job Type",
        ["All Types", "Full-time", "Part-time", "Contract"],
        label_visibility="collapsed",
    )
with fc4:
    exp_opt = st.selectbox(
        "Experience",
        ["All Levels", "Entry", "Junior", "Mid", "Senior", "Lead"],
        label_visibility="collapsed",
    )
with fc5:
    page_size = st.selectbox("Per page", [10, 20, 50], index=1, label_visibility="collapsed")

# ── Pagination state ──────────────────────────────────────────────────────────
if "jobs_page" not in st.session_state:
    st.session_state.jobs_page = 1

params: dict = {"page": st.session_state.jobs_page, "page_size": page_size}
if remote_opt == "Remote Only":
    params["remote"] = True
elif remote_opt == "On-site Only":
    params["remote"] = False

data      = api_get("/jobs/", params=params) or {}
all_items = data.get("items", [])
total     = data.get("total", 0)

# ── Client-side filtering ─────────────────────────────────────────────────────
items = all_items
if search_q:
    q     = search_q.lower()
    items = [
        j for j in items
        if q in j.get("title", "").lower()
        or q in j.get("company", "").lower()
        or q in j.get("description", "").lower()
        or any(q in s.lower() for s in (j.get("skills_required") or {}).get("required", []))
    ]
exp_map = {"Entry": "entry", "Junior": "junior", "Mid": "mid", "Senior": "senior", "Lead": "lead"}
if exp_opt in exp_map:
    items = [j for j in items if j.get("experience_level", "").lower() == exp_map[exp_opt]]

jtype_raw = {"Full-time": "full_time", "Part-time": "part_time", "Contract": "contract"}
if jtype_opt in jtype_raw:
    items = [j for j in items if j.get("job_type") == jtype_raw[jtype_opt]]

# ── Summary + pagination ──────────────────────────────────────────────────────
rc1, rc2, rc3 = st.columns([4, 1, 1])
rc1.markdown(
    f'<div style="font-size:13px;color:#64748B;padding:8px 0">'
    f'Showing <b style="color:#0F172A">{len(items)}</b> of '
    f'<b style="color:#0F172A">{total}</b> jobs</div>',
    unsafe_allow_html=True,
)
with rc2:
    if st.session_state.jobs_page > 1:
        if st.button("← Prev"):
            st.session_state.jobs_page -= 1
            st.rerun()
with rc3:
    if len(all_items) == page_size:
        if st.button("Next →"):
            st.session_state.jobs_page += 1
            st.rerun()

st.markdown(
    "<hr style='border:none;border-top:1px solid #E2E8F0;margin:6px 0 14px'>",
    unsafe_allow_html=True,
)

# ── Job cards ─────────────────────────────────────────────────────────────────
if not items:
    info_box("No jobs match your filters. Try broadening your search.", kind="info")
else:
    applied_ids: set = st.session_state.get("applied_job_ids", set())

    for job in items:
        posted  = job.get("posted_date")
        days_ago = ""
        if posted:
            try:
                dt       = datetime.fromisoformat(posted.replace("Z", "+00:00"))
                diff     = (datetime.now(timezone.utc) - dt).days
                days_ago = f"{diff}d ago" if diff > 1 else "Today"
            except Exception:
                pass

        match_score = job.get("match_score") or job.get("ats_score")
        if match_score and match_score <= 1.0:
            match_score = int(match_score * 100)

        st.markdown(
            job_card_html(job, match_score=match_score, applied=job["id"] in applied_ids),
            unsafe_allow_html=True,
        )

        with st.expander("View details & apply"):
            tab_desc, tab_apply = st.tabs(["📄 Job Description", "🚀 Apply Now"])

            with tab_desc:
                desc = job.get("description", "No description available.")
                st.markdown(
                    f"<div style='white-space:pre-wrap;font-size:14px;line-height:1.7;"
                    f"color:#374151'>{desc}</div>",
                    unsafe_allow_html=True,
                )
                skills_req  = (job.get("skills_required") or {}).get("required", [])
                skills_pref = (job.get("skills_required") or {}).get("preferred", [])
                if skills_req:
                    st.markdown("**Required skills:**")
                    st.markdown("  ".join(f"`{s}`" for s in skills_req))
                if skills_pref:
                    st.markdown("**Nice to have:**")
                    st.markdown("  ".join(f"`{s}`" for s in skills_pref))

            with tab_apply:
                st.markdown(
                    f"<div style='font-size:15px;font-weight:700;color:#0F172A;margin-bottom:8px'>"
                    f"Apply to: {job.get('title','')} at {job.get('company','')}</div>",
                    unsafe_allow_html=True,
                )
                apply_mode = st.radio(
                    "Application Mode",
                    ["review", "autonomous", "batch"],
                    horizontal=True,
                    key=f"mode_{job['id']}",
                    help=(
                        "review: you approve each step · "
                        "autonomous: AI applies automatically · "
                        "batch: queue then apply in bulk"
                    ),
                )
                if st.button("🚀 Submit Application", key=f"apply_{job['id']}", type="primary"):
                    result = api_post("/applications/", {"job_id": job["id"], "apply_mode": apply_mode})
                    if result:
                        applied_ids.add(job["id"])
                        st.session_state.applied_job_ids = applied_ids
                        info_box(f"Application submitted! ID: {str(result.get('id','?'))[:8]}…", kind="success")
                        st.balloons()
