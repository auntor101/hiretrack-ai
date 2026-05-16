"""Settings page — configure the HireTrack AI pipeline.
Drop-in replacement: uses ht_components for branded visuals.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import api_get, api_put
from ht_components import (
    inject_global_css, page_header, section_header,
    info_box, ai_callout,
    HT_COLORS, HT_STATUS,
)

st.set_page_config(
    page_title="Settings · HireTrack AI",
    page_icon="⚙️",
    layout="wide",
)
inject_global_css()
page_header("Settings", "Configure your HireTrack AI pipeline.")

settings  = api_get("/settings") or {}
providers = api_get("/settings/llm-providers") or []

tab1, tab2, tab3, tab4 = st.tabs(["🤖 Pipeline", "🔑 LLM Providers", "👤 Candidate Profile", "📄 Templates"])

# ── Pipeline ──────────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        section_header("Application Mode")
        mode_options = ["review", "autonomous", "batch"]
        current_mode = settings.get("apply_mode", "review")
        mode_idx     = mode_options.index(current_mode) if current_mode in mode_options else 0
        apply_mode   = st.radio(
            "Mode",
            mode_options,
            index=mode_idx,
            format_func=lambda x: {
                "review":     "👀 Review — approve each application manually",
                "autonomous": "🤖 Autonomous — AI applies automatically",
                "batch":      "📦 Batch — queue then apply in bulk",
            }[x],
        )

        section_header("Quality Gate")
        min_ats = st.slider(
            "Minimum ATS Score",
            min_value=0.0, max_value=1.0,
            value=float(settings.get("min_ats_score", 0.75)),
            step=0.05, format="%.0f%%",
            help="Only apply to jobs where your resume scores above this threshold.",
        )
        st.caption(f"Jobs scoring below {min_ats:.0%} will be skipped automatically.")

        section_header("Parallelism")
        max_parallel = st.slider(
            "Max parallel applications",
            min_value=1, max_value=5,
            value=int(settings.get("max_parallel", 3)),
        )

    with col2:
        section_header("Platforms")
        ALL_PLATFORMS = ["linkedin", "indeed", "glassdoor", "bdjobs", "talently"]
        PLATFORM_ICONS = {"linkedin": "🔗", "indeed": "💻", "glassdoor": "🏢", "bdjobs": "🇧🇩", "talently": "⭐"}
        enabled_set  = set(settings.get("platforms_enabled", ["linkedin", "indeed", "glassdoor"]))
        selected_platforms = []
        for p in ALL_PLATFORMS:
            icon    = PLATFORM_ICONS.get(p, "")
            checked = st.checkbox(f"{icon} {p.title()}", value=p in enabled_set, key=f"plat_{p}")
            if checked:
                selected_platforms.append(p)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save Pipeline Settings", type="primary"):
        res = api_put("/settings", {
            "apply_mode": apply_mode,
            "min_ats_score": min_ats,
            "max_parallel": max_parallel,
            "platforms_enabled": selected_platforms,
        })
        if res:
            info_box("Pipeline settings saved.", kind="success")

# ── LLM Providers ─────────────────────────────────────────────────────────────
with tab2:
    section_header("Configured LLM Providers")

    PROVIDER_ICONS = {
        "groq": "⚡", "openai": "🤖", "gemini": "♊",
        "openrouter": "🔀", "github": "🐙", "portkey": "🔑",
    }

    if providers:
        cols = st.columns(3)
        for i, p in enumerate(providers):
            icon        = PROVIDER_ICONS.get(p.get("provider", "").lower(), "🔌")
            configured  = p.get("configured", False)
            is_primary  = p.get("is_primary", False)
            sc          = HT_COLORS["success"] if configured else HT_COLORS["error"]
            primary_html = (
                f'<span style="background:{HT_COLORS["blue_500"]};color:white;'
                f'padding:1px 10px;border-radius:999px;font-size:10.5px;font-weight:700">Primary</span>'
                if is_primary else ""
            )
            with cols[i % 3]:
                st.markdown(
                    f"""<div style="background:white;border-radius:14px;padding:18px 20px;
                        box-shadow:0 0 0 1px rgba(15,23,42,0.05),0 2px 8px rgba(15,23,42,0.04);
                        margin-bottom:12px;border-top:3px solid {sc}">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                            <span style="font-size:24px">{icon}</span>
                            {primary_html}
                        </div>
                        <div style="font-size:16px;font-weight:700;color:#0F172A;margin-bottom:2px">
                            {p.get('provider','').title()}
                        </div>
                        <div style="font-size:12px;color:#64748B;margin-bottom:10px">
                            {p.get('model','')}
                        </div>
                        <div style="font-size:12px;font-weight:600;color:{sc}">
                            {'✅ Configured' if configured else '❌ Not configured'}
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    else:
        info_box("No provider data available.")

    ai_callout(
        "Set API keys in your .env file: LLM__GROQ_API_KEY, LLM__OPENAI_API_KEY, "
        "LLM__OPENROUTER_API_KEY, etc. See .env.example for the full list.",
        title="Configuration",
    )

# ── Candidate Profile ─────────────────────────────────────────────────────────
with tab3:
    profile = settings.get("candidate_profile", {}) or {}

    section_header("Personal Information")
    pc1, pc2 = st.columns(2)
    with pc1:
        full_name = st.text_input("Full Name",   value=profile.get("full_name", ""))
        email     = st.text_input("Email",        value=profile.get("email", ""))
        phone     = st.text_input("Phone",        value=profile.get("phone", ""))
    with pc2:
        location    = st.text_input("Location",     value=profile.get("location", ""))
        linkedin    = st.text_input("LinkedIn URL", value=profile.get("linkedin_url", ""))
        github      = st.text_input("GitHub URL",   value=profile.get("github_url", ""))

    summary    = st.text_area("Professional Summary", value=profile.get("summary", ""), height=100)
    skills_raw = st.text_input(
        "Skills (comma-separated)",
        value=", ".join(profile.get("skills", [])),
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save Profile", type="primary"):
        skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
        res = api_put("/settings", {
            "candidate_profile": {
                "full_name": full_name, "email": email, "phone": phone,
                "location": location, "linkedin_url": linkedin, "github_url": github,
                "summary": summary, "skills": skills_list,
                "experience":     profile.get("experience", []),
                "education":      profile.get("education", []),
                "certifications": profile.get("certifications", []),
            }
        })
        if res:
            info_box("Profile saved.", kind="success")

# ── Templates ─────────────────────────────────────────────────────────────────
with tab4:
    RESUME_TEMPLATES = [
        {"id": "modern",    "icon": "🎨", "name": "Modern",    "desc": "Clean lines, blue accent sidebar, skills panel"},
        {"id": "classic",   "icon": "📰", "name": "Classic",   "desc": "Traditional layout, highly ATS-optimised"},
        {"id": "creative",  "icon": "✨", "name": "Creative",  "desc": "Bold header, visual skill bars, colour accents"},
        {"id": "executive", "icon": "💼", "name": "Executive", "desc": "Sophisticated two-column, leadership focus"},
        {"id": "minimal",   "icon": "⬜", "name": "Minimal",   "desc": "Ultra-clean typography, no distractions"},
    ]
    CL_TEMPLATES = [
        {"id": "standard",  "icon": "📝", "name": "Standard",  "desc": "Professional and versatile for any industry"},
        {"id": "technical", "icon": "💻", "name": "Technical", "desc": "Highlights tech skills, metrics-forward"},
        {"id": "creative",  "icon": "🎭", "name": "Creative",  "desc": "Expressive tone for design & creative roles"},
    ]

    cur_rtpl = st.session_state.get("default_resume_template", "modern")
    cur_cltpl = st.session_state.get("default_cl_template", "standard")

    section_header("Resume Template")
    rcols = st.columns(5)
    for col, tpl in zip(rcols, RESUME_TEMPLATES):
        is_sel = tpl["id"] == cur_rtpl
        col.markdown(
            f"""<div style="background:{'rgba(10,102,194,0.08)' if is_sel else 'white'};
                border:2px solid {'#0A66C2' if is_sel else '#E2E8F0'};
                border-radius:14px;padding:18px 12px;text-align:center;
                transition:all 200ms ease;margin-bottom:8px">
                <div style="font-size:28px;margin-bottom:8px">{tpl['icon']}</div>
                <div style="font-size:13px;font-weight:{'700' if is_sel else '600'};
                     color:{'#0A66C2' if is_sel else '#0F172A'}">{tpl['name']}</div>
                <div style="font-size:11px;color:#64748B;margin-top:4px;line-height:1.4">{tpl['desc']}</div>
                {'<div style="margin-top:8px;font-size:10px;font-weight:700;color:#0A66C2;letter-spacing:0.05em">✓ ACTIVE</div>' if is_sel else ''}
            </div>""",
            unsafe_allow_html=True,
        )
        if col.button("Select", key=f"rtpl_{tpl['id']}", use_container_width=True,
                      type="primary" if is_sel else "secondary"):
            st.session_state["default_resume_template"] = tpl["id"]
            st.rerun()

    st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
    info_box(f"Active resume template: **{cur_rtpl.title()}** — used when generating resumes this session.", kind="success")

    section_header("Cover Letter Template")
    clcols = st.columns(3)
    for col, tpl in zip(clcols, CL_TEMPLATES):
        is_sel = tpl["id"] == cur_cltpl
        col.markdown(
            f"""<div style="background:{'rgba(124,58,237,0.07)' if is_sel else 'white'};
                border:2px solid {'#7C3AED' if is_sel else '#E2E8F0'};
                border-radius:14px;padding:20px 14px;text-align:center;
                transition:all 200ms ease;margin-bottom:8px">
                <div style="font-size:32px;margin-bottom:8px">{tpl['icon']}</div>
                <div style="font-size:14px;font-weight:{'700' if is_sel else '600'};
                     color:{'#7C3AED' if is_sel else '#0F172A'}">{tpl['name']}</div>
                <div style="font-size:12px;color:#64748B;margin-top:5px;line-height:1.4">{tpl['desc']}</div>
                {'<div style="margin-top:8px;font-size:10px;font-weight:700;color:#7C3AED;letter-spacing:0.05em">✓ ACTIVE</div>' if is_sel else ''}
            </div>""",
            unsafe_allow_html=True,
        )
        if col.button("Select", key=f"cltpl_{tpl['id']}", use_container_width=True,
                      type="primary" if is_sel else "secondary"):
            st.session_state["default_cl_template"] = tpl["id"]
            st.rerun()

    st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
    info_box(f"Active cover letter template: **{cur_cltpl.title()}** — used when generating cover letters this session.", kind="success")
    info_box("Persistent template preferences require a backend schema update. Session defaults reset on page reload.", kind="info")
