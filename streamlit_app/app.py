"""HireTrack AI — Streamlit dashboard.

Connects to the FastAPI backend at the URL from the API_BASE_URL environment
variable (default: http://localhost:8000/api/v1) and renders a real-time
view of the job application pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from utils import API_BASE, api_get, api_post  # noqa: E402


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="HireTrack AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("HireTrack AI")
st.sidebar.caption("AI-powered job application pipeline")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Applications", "Jobs", "Add Job"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.markdown("**Backend**")
st.sidebar.code(API_BASE, language=None)

# ---------------------------------------------------------------------------
# Dashboard page
# ---------------------------------------------------------------------------

if page == "Dashboard":
    st.title("Pipeline Overview")

    stats = _get("/dashboard/stats") or {}
    total = stats.get("total_applications", 0)
    by_status: dict[str, int] = stats.get("by_status", {})
    avg_ats: float = stats.get("avg_ats_score", 0.0)
    top_missing: list[dict] = stats.get("top_missing_skills", [])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", total)
    col2.metric("Interviews", by_status.get("interview", 0))
    col3.metric("Offers", by_status.get("offer", 0))
    col4.metric("Avg ATS Score", f"{avg_ats:.1f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Applications by Status")
        if by_status:
            status_df = pd.DataFrame(
                list(by_status.items()), columns=["Status", "Count"]
            ).sort_values("Count", ascending=False)
            st.bar_chart(status_df.set_index("Status"))
        else:
            st.info("No applications yet.")

    with col_right:
        st.subheader("Top Missing Skills")
        if top_missing:
            skills_df = pd.DataFrame(top_missing).rename(
                columns={"skill": "Skill", "count": "Frequency"}
            )
            st.bar_chart(skills_df.set_index("Skill"))
        else:
            st.info("No skill-gap analyses run yet.")

# ---------------------------------------------------------------------------
# Applications page
# ---------------------------------------------------------------------------

elif page == "Applications":
    st.title("Applications")

    status_filter = st.selectbox(
        "Filter by status",
        ["all", "queued", "pending_review", "approved", "applied",
         "interview", "offer", "rejected", "withdrawn", "failed"],
        index=0,
    )

    params: dict = {"page": 1, "page_size": 100}
    if status_filter != "all":
        params["status"] = status_filter

    data = api_get("/applications/", params=params) or {}
    items: list[dict] = data.get("items", [])

    if not items:
        st.info("No applications found.")
    else:
        df = pd.DataFrame(items)
        display_cols = [c for c in
                        ["id", "job_id", "status", "apply_mode", "ats_score", "created_at"]
                        if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)

        st.caption(f"{data.get('total', len(items))} total applications")

        # CSV export
        csv_url = f"{API_BASE}/applications/export"
        st.markdown(f"[Download CSV]({csv_url})", unsafe_allow_html=True)

    st.divider()
    st.subheader("Run actions on a single application")

    app_id = st.text_input("Application ID", placeholder="Paste an application UUID here")
    action = st.selectbox("Action", ["score-resume", "skill-gap", "cover-letter"])

    if st.button("Run") and app_id.strip():
        result = api_post(f"/applications/{app_id.strip()}/{action}")
        if result:
            st.json(result)

# ---------------------------------------------------------------------------
# Jobs page
# ---------------------------------------------------------------------------

elif page == "Jobs":
    st.title("Jobs")

    data = api_get("/jobs/", params={"page": 1, "page_size": 100}) or {}
    items = data.get("items", [])

    if not items:
        st.info("No jobs found.  Use 'Add Job' to create one, or run a search.")
    else:
        df = pd.DataFrame(items)
        display_cols = [c for c in
                        ["id", "title", "company", "location", "status",
                         "match_score", "platform", "created_at"]
                        if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)

    st.divider()
    st.subheader("Search for jobs via Exa")
    query = st.text_input("Keywords", placeholder="e.g. Machine Learning Engineer Dhaka")
    if st.button("Search") and query.strip():
        results = api_post("/jobs/search", json={"query": query.strip(), "num_results": 10})
        if results:
            job_items = results.get("items", [])
            st.success(f"Found {len(job_items)} jobs")
            if job_items:
                st.dataframe(pd.DataFrame(job_items), use_container_width=True)

# ---------------------------------------------------------------------------
# Add Job page
# ---------------------------------------------------------------------------

elif page == "Add Job":
    st.title("Add a Job Manually")

    with st.form("add_job_form"):
        title = st.text_input("Job Title *")
        company = st.text_input("Company *")
        location = st.text_input("Location", value="Dhaka, Bangladesh")
        url = st.text_input("Job URL *")
        description = st.text_area("Job Description", height=200)
        job_type = st.selectbox("Type", ["full_time", "part_time", "contract", "internship"])
        remote = st.checkbox("Remote / Hybrid")
        submitted = st.form_submit_button("Save Job")

    if submitted:
        if not (title and company and url):
            st.error("Title, Company, and URL are required.")
        else:
            payload = {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "description": description,
                "job_type": job_type,
                "remote": remote,
            }
            result = api_post("/jobs/", json=payload)
            if result:
                st.success(f"Job saved! ID: {result.get('id')}")
                st.json(result)
