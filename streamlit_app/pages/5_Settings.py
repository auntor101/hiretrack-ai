"""Settings page -- configure AutoApply AI pipeline behaviour."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import api_get, api_put, inject_global_css

st.set_page_config(
    page_title="Settings \u00b7 AutoApply AI",
    page_icon="\u2699\ufe0f",
    layout="wide",
)
inject_global_css()

st.markdown('<div class="page-title">\u2699\ufe0f Settings</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Configure your AutoApply AI pipeline</div>',
    unsafe_allow_html=True,
)

settings = api_get("/settings") or {}
providers = api_get("/settings/llm-providers") or []

tab1, tab2, tab3 = st.tabs(
    ["\U0001f916 Pipeline", "\U0001f511 LLM Providers", "\U0001f464 Candidate Profile"]
)

# ── Tab 1: Pipeline ────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Application Mode</div>', unsafe_allow_html=True)
        mode_options = ["review", "autonomous", "batch"]
        current_mode = settings.get("apply_mode", "review")
        mode_idx = mode_options.index(current_mode) if current_mode in mode_options else 0
        apply_mode = st.radio(
            "Mode",
            mode_options,
            index=mode_idx,
            format_func=lambda x: {
                "review": "\U0001f440 Review -- approve each application manually",
                "autonomous": "\U0001f916 Autonomous -- AI applies automatically",
                "batch": "\U0001f4e6 Batch -- queue then apply in bulk",
            }[x],
        )

        st.markdown('<div class="section-title">Quality Gate</div>', unsafe_allow_html=True)
        min_ats = st.slider(
            "Minimum ATS Score",
            min_value=0.0,
            max_value=1.0,
            value=float(settings.get("min_ats_score", 0.75)),
            step=0.05,
            format="%.0f%%",
            help="Only apply to jobs where your resume scores above this threshold",
        )
        st.caption(
            f"Only apply when ATS score \u2265 {min_ats:.0%} -- "
            "jobs below this will be skipped automatically."
        )

        st.markdown('<div class="section-title">Parallelism</div>', unsafe_allow_html=True)
        max_parallel = st.slider(
            "Max parallel applications",
            min_value=1,
            max_value=5,
            value=int(settings.get("max_parallel", 3)),
            help="Number of browser sessions to run simultaneously",
        )

    with col2:
        st.markdown('<div class="section-title">Enabled Platforms</div>', unsafe_allow_html=True)
        ALL_PLATFORMS = ["linkedin", "indeed", "glassdoor", "bdjobs", "talently"]
        PLATFORM_ICONS = {
            "linkedin": "\U0001f517", "indeed": "\U0001f4bb",
            "glassdoor": "\U0001f3e2", "bdjobs": "\U0001f1e7\U0001f1e9",
            "talently": "\U0001f31f",
        }
        enabled_set = set(settings.get("platforms_enabled", ["linkedin", "indeed", "glassdoor"]))
        selected_platforms = []
        for p in ALL_PLATFORMS:
            icon = PLATFORM_ICONS.get(p, "")
            checked = st.checkbox(f"{icon} {p.title()}", value=p in enabled_set, key=f"plat_{p}")
            if checked:
                selected_platforms.append(p)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("\U0001f4be Save Pipeline Settings", type="primary"):
        res = api_put("/settings", {
            "apply_mode": apply_mode,
            "min_ats_score": min_ats,
            "max_parallel": max_parallel,
            "platforms_enabled": selected_platforms,
        })
        if res:
            st.success("Pipeline settings saved!")

# ── Tab 2: LLM Providers ──────────────────────────────────────────────────────
with tab2:
    st.markdown(
        '<div class="section-title">Configured LLM Providers</div>',
        unsafe_allow_html=True,
    )
    PROVIDER_ICONS = {
        "groq": "\u26a1", "openai": "\U0001f916", "gemini": "\u264a",
        "openrouter": "\U0001f500", "github": "\U0001f419", "portkey": "\U0001f511",
    }
    if providers:
        cols = st.columns(3)
        for i, p in enumerate(providers):
            icon = PROVIDER_ICONS.get(p.get("provider", "").lower(), "\U0001f50c")
            configured = p.get("configured", False)
            is_primary = p.get("is_primary", False)
            status_color = "#22C55E" if configured else "#EF4444"
            status_text = "Configured" if configured else "Not configured"
            primary_badge = (
                '<span style="background:#0A66C2;color:white;padding:1px 8px;'
                'border-radius:999px;font-size:11px;font-weight:600">Primary</span>'
                if is_primary
                else ""
            )
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="background:white;border-radius:12px;padding:20px;
                                box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:12px;
                                border-top:3px solid {status_color}">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div style="font-size:22px">{icon}</div>
                            {primary_badge}
                        </div>
                        <div style="font-size:16px;font-weight:700;color:#111827;margin:8px 0 4px">
                            {p.get('provider','').title()}
                        </div>
                        <div style="font-size:12px;color:#6B7280;margin-bottom:8px">
                            {p.get('model','')}
                        </div>
                        <div style="font-size:12px;font-weight:600;color:{status_color}">
                            {'&#x2705;' if configured else '&#x274C;'} {status_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No provider data available.")

    st.markdown(
        '<div class="info-box">Set API keys in your <code>.env</code> file: '
        "<code>LLM__GROQ_API_KEY</code>, <code>LLM__OPENAI_API_KEY</code>, "
        "<code>LLM__OPENROUTER_API_KEY</code>, etc.</div>",
        unsafe_allow_html=True,
    )

# ── Tab 3: Candidate Profile ───────────────────────────────────────────────────
with tab3:
    profile = settings.get("candidate_profile", {}) or {}

    st.markdown(
        '<div class="section-title">Personal Information</div>',
        unsafe_allow_html=True,
    )
    pc1, pc2 = st.columns(2)
    with pc1:
        full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
        email = st.text_input("Email", value=profile.get("email", ""))
        phone = st.text_input("Phone", value=profile.get("phone", ""))
    with pc2:
        location = st.text_input("Location", value=profile.get("location", ""))
        linkedin_url = st.text_input("LinkedIn URL", value=profile.get("linkedin_url", ""))
        github_url = st.text_input("GitHub URL", value=profile.get("github_url", ""))

    summary = st.text_area(
        "Professional Summary", value=profile.get("summary", ""), height=100
    )
    skills_raw = st.text_input(
        "Skills (comma-separated)",
        value=", ".join(profile.get("skills", [])),
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("\U0001f4be Save Profile", type="primary"):
        skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
        res = api_put("/settings", {
            "candidate_profile": {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "location": location,
                "linkedin_url": linkedin_url,
                "github_url": github_url,
                "summary": summary,
                "skills": skills_list,
                "experience": profile.get("experience", []),
                "education": profile.get("education", []),
                "certifications": profile.get("certifications", []),
            }
        })
        if res:
            st.success("Profile saved!")
