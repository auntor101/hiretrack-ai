"""Resume upload & ATS scoring page."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import api_get, api_post, api_upload, cold_start_guard
from ht_components import (
    inject_global_css, page_header, section_header,
    skill_tags_html, info_box, ai_callout,
    HT_COLORS,
)

st.set_page_config(
    page_title="Resume & ATS · HireTrack AI",
    page_icon="📄",
    layout="wide",
)
inject_global_css()
cold_start_guard()
page_header("Resume & ATS Scorer", "Upload your CV and score it against any job description.")

left, right = st.columns([1, 1], gap="large")

# ── Left: Upload + Resume list ────────────────────────────────────────────────
with left:
    section_header("Upload CV")
    uploaded_file = st.file_uploader(
        "Drop your resume here",
        type=["pdf", "docx"],
        help="PDF or DOCX · max 10 MB",
        label_visibility="collapsed",
    )

    if uploaded_file:
        info_box(f"📎  {uploaded_file.name}  ({uploaded_file.size // 1024} KB)", kind="info")
        if st.button("📤 Upload & Parse Resume", type="primary", use_container_width=True):
            with st.spinner("Uploading and parsing…"):
                res = api_upload(
                    "/resumes/upload",
                    file_bytes=uploaded_file.read(),
                    filename=uploaded_file.name,
                    content_type=uploaded_file.type or "application/octet-stream",
                )
            if res:
                st.session_state["resume_id"]     = res["id"]
                st.session_state["resume_name"]   = res["name"]
                st.session_state["resume_skills"] = res.get("skills_detected", [])
                st.session_state.pop("last_score", None)
                info_box(
                    f"Uploaded! Detected **{res['word_count']}** words and "
                    f"**{len(res.get('skills_detected', []))}** skills.",
                    kind="success",
                )
                st.rerun()

    resume_id = st.session_state.get("resume_id")

    if resume_id:
        st.markdown(
            f"""<div style="background:rgba(5,150,105,0.08);border:1.5px solid rgba(5,150,105,0.25);
            border-radius:12px;padding:14px 16px;margin:12px 0">
            <div style="font-size:11px;font-weight:700;color:#059669;letter-spacing:0.06em;
            text-transform:uppercase">✓ Active Resume</div>
            <div style="font-size:15px;font-weight:700;color:#0F172A;margin-top:4px">
            {st.session_state.get('resume_name','')}</div></div>""",
            unsafe_allow_html=True,
        )
        skills = st.session_state.get("resume_skills", [])
        if skills:
            section_header("Detected Skills")
            st.markdown(skill_tags_html(skills, limit=30), unsafe_allow_html=True)

    section_header("All Resumes")
    rd = api_get("/resumes/") or {}
    resumes = rd.get("items", [])
    if resumes:
        for r in resumes:
            active = r["id"] == resume_id
            ats_txt = f"{int(r['ats_score'] * 100)}%" if r.get("ats_score") else "Not scored"
            st.markdown(
                f"""<div style="background:{'rgba(10,102,194,0.06)' if active else 'white'};
                border:1.5px solid {'#0A66C2' if active else '#E2E8F0'};border-radius:10px;
                padding:12px 16px;margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="font-size:13px;font-weight:600;color:#0F172A">{r['name']}</div>
                    <div style="font-size:11px;color:#64748B">{r['type'].title()} · ATS: {ats_txt}</div>
                  </div>
                  {'<span style="font-size:10px;font-weight:700;color:#0A66C2;letter-spacing:0.05em">ACTIVE</span>' if active else ''}
                </div></div>""",
                unsafe_allow_html=True,
            )
            if not active:
                if st.button("Use this", key=f"use_{r['id']}", use_container_width=True):
                    st.session_state["resume_id"]     = r["id"]
                    st.session_state["resume_name"]   = r["name"]
                    st.session_state["resume_skills"] = []
                    st.session_state.pop("last_score", None)
                    st.rerun()
    else:
        info_box("No resumes yet — upload one above.")

# ── Right: Job selector + Score ───────────────────────────────────────────────
with right:
    section_header("Score Against a Job")

    jobs_data = api_get("/jobs/", params={"page_size": 100}) or {}
    jobs = jobs_data.get("items", [])

    if not jobs:
        info_box("No jobs in the system yet. Go to Job Board and load demo data first.", kind="warning")
    else:
        job_map = {f"{j['title']}  @  {j['company']}": j for j in jobs}
        chosen_label = st.selectbox("Select job", list(job_map.keys()), label_visibility="collapsed")
        chosen_job   = job_map[chosen_label]

        exp    = chosen_job.get("experience_level", "")
        salary = chosen_job.get("salary_range", "")
        remote = "🌐 Remote" if chosen_job.get("remote") else "🏢 On-site"
        loc    = chosen_job.get("location", "")
        st.markdown(
            f"""<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
            padding:12px 16px;margin:6px 0 14px;font-size:12px;color:#64748B;
            display:flex;gap:18px;flex-wrap:wrap">
            <span>📍 {loc}</span>
            {'<span>💰 '+salary+'</span>' if salary else ''}
            <span>{remote}</span>
            {'<span>⭐ '+exp.title()+'</span>' if exp else ''}
            </div>""",
            unsafe_allow_html=True,
        )

        req_skills = (chosen_job.get("skills_required") or {}).get("required", [])
        if req_skills:
            st.markdown(
                f"**Required:** " + "  ".join(f"`{s}`" for s in req_skills[:10])
            )

        no_resume = not st.session_state.get("resume_id")
        if no_resume:
            info_box("Upload or select a resume on the left first.", kind="warning")

        if st.button("🎯 Score My Resume", type="primary", use_container_width=True,
                     disabled=no_resume):
            with st.spinner("Scoring against job description…"):
                result = api_post(
                    f"/resumes/{st.session_state['resume_id']}/score",
                    {"job_id": chosen_job["id"]},
                )
            if result:
                st.session_state["last_score"]     = result
                st.session_state["last_score_job"] = chosen_label
                st.rerun()

        score = st.session_state.get("last_score")
        if score:
            overall = score.get("overall_score", 0)
            color   = "#059669" if overall >= 75 else "#D97706" if overall >= 50 else "#DC2626"
            verdict = "Excellent match! 🎉" if overall >= 75 else "Good potential 👍" if overall >= 50 else "Needs work 📝"

            st.markdown(
                f"""<div style="text-align:center;padding:28px 20px;background:white;
                border-radius:16px;box-shadow:0 0 0 1px rgba(15,23,42,0.05),
                0 6px 24px rgba(15,23,42,0.07);margin:14px 0">
                <div style="font-size:72px;font-weight:900;color:{color};line-height:1">
                {int(overall)}</div>
                <div style="font-size:13px;color:#64748B;margin-top:6px">ATS Score / 100</div>
                <div style="font-size:17px;font-weight:700;color:{color};margin-top:10px">
                {verdict}</div>
                <div style="font-size:12px;color:#94A3B8;margin-top:4px">
                vs. {st.session_state.get('last_score_job','').split('@')[0].strip()}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            section_header("Score Breakdown")
            for label, key, col in [
                ("Skills Match",     "skill_score",       HT_COLORS["blue_500"]),
                ("Experience Match", "experience_score",  HT_COLORS["violet_500"]),
                ("Education Match",  "education_score",   HT_COLORS["success"]),
                ("Keyword Coverage", "keyword_score",     HT_COLORS["warning"]),
            ]:
                pct = int(score.get(key, 0))
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'font-size:13px;font-weight:500;color:#374151;margin-bottom:3px">'
                    f'<span>{label}</span>'
                    f'<span style="font-weight:700;color:{col}">{pct}%</span></div>',
                    unsafe_allow_html=True,
                )
                st.progress(pct / 100)

            missing = score.get("missing_skills", [])
            if missing:
                section_header("Missing Skills")
                st.markdown(skill_tags_html(missing, missing=missing, limit=20), unsafe_allow_html=True)

            suggestions = score.get("suggestions", [])
            if suggestions:
                section_header("AI Recommendations")
                ai_callout("\n".join(f"• {s}" for s in suggestions))
