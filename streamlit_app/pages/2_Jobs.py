"""Job listings page -- browse, filter, and apply to jobs."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import (
    JOB_TYPE_LABELS,
    api_get,
    api_post,
    exp_badge_html,
    inject_global_css,
    skill_tags_html,
)

st.set_page_config(
    page_title="Jobs \u00b7 AutoApply AI",
    page_icon="\U0001f4bc",
    layout="wide",
)
inject_global_css()

st.markdown('<div class="page-title">\U0001f4bc Job Listings</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Browse and apply to curated tech opportunities in Bangladesh</div>',
    unsafe_allow_html=True,
)

# ── Filters ───────────────────────────────────────────────────────────────────
fc1, fc2, fc3, fc4, fc5 = st.columns([3, 1, 1, 1, 1])
with fc1:
    search_q = st.text_input(
        "",
        placeholder="\U0001f50d  Search by title, company, or skill...",
        label_visibility="collapsed",
    )
with fc2:
    remote_opt = st.selectbox(
        "Location", ["All", "Remote Only", "On-site Only"], label_visibility="collapsed"
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
        ["All Levels", "Junior", "Mid", "Senior"],
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

data = api_get("/jobs/", params=params) or {}
all_items: list[dict] = data.get("items", [])
total = data.get("total", 0)

# ── Client-side filtering ──────────────────────────────────────────────────────
items = all_items
if search_q:
    q = search_q.lower()
    items = [
        j for j in items
        if q in j.get("title", "").lower()
        or q in j.get("company", "").lower()
        or q in j.get("description", "").lower()
        or any(
            q in s.lower()
            for s in (j.get("skills_required") or {}).get("required", [])
        )
    ]
exp_map = {"Junior": "junior", "Mid": "mid", "Senior": "senior"}
if exp_opt in exp_map:
    items = [j for j in items if j.get("experience_level") == exp_map[exp_opt]]

jtype_raw = {"Full-time": "full_time", "Part-time": "part_time", "Contract": "contract"}
if jtype_opt in jtype_raw:
    items = [j for j in items if j.get("job_type") == jtype_raw[jtype_opt]]

# ── Summary + pagination buttons ─────────────────────────────────────────────
rc1, rc2, rc3 = st.columns([3, 1, 1])
rc1.markdown(
    f'<div style="font-size:14px;color:#6B7280;padding:8px 0">'
    f'Showing <strong>{len(items)}</strong> of <strong>{total}</strong> jobs</div>',
    unsafe_allow_html=True,
)
with rc2:
    if st.session_state.jobs_page > 1:
        if st.button("\u2190 Prev page"):
            st.session_state.jobs_page -= 1
            st.rerun()
with rc3:
    if len(all_items) == page_size:
        if st.button("Next page \u2192"):
            st.session_state.jobs_page += 1
            st.rerun()

st.markdown(
    "<hr style='border:none;border-top:1px solid #E5E7EB;margin:8px 0 16px'>",
    unsafe_allow_html=True,
)

# ── Job Cards ─────────────────────────────────────────────────────────────────
if not items:
    st.markdown(
        '<div class="info-box">No jobs match your filters. Try broadening your search.</div>',
        unsafe_allow_html=True,
    )
else:
    for job in items:
        skills_req: list[str] = (job.get("skills_required") or {}).get("required", [])
        skills_pref: list[str] = (job.get("skills_required") or {}).get("preferred", [])
        all_skills = skills_req + skills_pref

        posted = job.get("posted_date")
        days_ago = ""
        if posted:
            try:
                dt = datetime.fromisoformat(posted.replace("Z", "+00:00"))
                diff = (datetime.now(timezone.utc) - dt).days
                days_ago = f"{diff}d ago" if diff > 1 else "Today"
            except Exception:
                pass

        remote_html = (
            '<span class="remote-badge">\U0001f310 Remote</span>'
            if job.get("remote")
            else '<span class="jobtype-badge">\U0001f3e2 On-site</span>'
        )
        jtype_label = JOB_TYPE_LABELS.get(job.get("job_type", ""), job.get("job_type", ""))
        salary = job.get("salary_range") or ""
        exp_html = exp_badge_html(job.get("experience_level"))

        st.markdown(
            f"""
            <div class="job-card">
                <div class="job-title">{job.get('title', '')}</div>
                <div class="job-company">{job.get('company', '')}</div>
                <div class="job-meta">
                    <span>\U0001f4cd {job.get('location', '')}</span>
                    {f'<span class="job-salary">\U0001f4b0 {salary}</span>' if salary else ''}
                    <span>{remote_html}</span>
                    <span><span class="jobtype-badge">{jtype_label}</span></span>
                    {f'<span>{exp_html}</span>' if exp_html else ''}
                    {f'<span>\U0001f552 {days_ago}</span>' if days_ago else ''}
                </div>
                <div style="margin-top:10px">{skill_tags_html(all_skills)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("View details & Apply"):
            tab_desc, tab_apply = st.tabs(["\U0001f4c4 Job Description", "\U0001f680 Apply Now"])

            with tab_desc:
                desc_text = job.get("description", "No description available.")
                st.markdown(
                    f"<div style='white-space:pre-wrap;font-size:14px;line-height:1.7;"
                    f"color:#374151'>{desc_text}</div>",
                    unsafe_allow_html=True,
                )
                if skills_req:
                    st.markdown("**Required Skills:**")
                    st.markdown("  ".join(f"`{s}`" for s in skills_req))
                if skills_pref:
                    st.markdown("**Nice to Have:**")
                    st.markdown("  ".join(f"`{s}`" for s in skills_pref))

            with tab_apply:
                st.markdown(
                    f"<div style='font-size:15px;font-weight:700;color:#111827;margin-bottom:8px'>"
                    f"Apply to: {job.get('title', '')} at {job.get('company', '')}</div>",
                    unsafe_allow_html=True,
                )
                apply_mode = st.radio(
                    "Application Mode",
                    ["review", "autonomous", "batch"],
                    horizontal=True,
                    key=f"mode_{job['id']}",
                    help=(
                        "review: you approve each step | "
                        "autonomous: AI applies automatically | "
                        "batch: queue then apply in bulk"
                    ),
                )
                if st.button(
                    "\U0001f680 Submit Application",
                    key=f"apply_{job['id']}",
                    type="primary",
                ):
                    result = api_post(
                        "/applications/",
                        {"job_id": job["id"], "apply_mode": apply_mode},
                    )
                    if result:
                        st.success(
                            f"Application submitted! ID: {str(result.get('id','?'))[:8]}..."
                        )
                        st.balloons()
