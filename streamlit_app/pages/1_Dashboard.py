"""Dashboard page — pipeline overview with KPIs and charts.
Drop-in replacement: uses ht_components for branded visuals.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st
from utils import api_get
from ht_components import (
    inject_global_css, page_header, section_header,
    kpi_row, dark_hero, style_plotly, info_box,
    skill_tags_html, HT_COLORS, HT_CHART_COLORS, HT_STATUS,
)

st.set_page_config(
    page_title="Dashboard · HireTrack AI",
    page_icon="📋",
    layout="wide",
)
inject_global_css()

# ── Data ──────────────────────────────────────────────────────────────────────
stats      = api_get("/analytics/dashboard") or {}
dash       = api_get("/dashboard/stats") or {}
funnel     = api_get("/analytics/funnel") or []
ats_data   = api_get("/analytics/ats-scores") or []
timeline   = api_get("/analytics/timeline") or []

# ── Hero ──────────────────────────────────────────────────────────────────────
hero_stats = [
    {"value": stats.get("total_applications", 0),  "label": "Applications"},
    {"value": stats.get("applications_interview", 0), "label": "Interviews"},
    {"value": stats.get("applications_offer", 0),   "label": "Offers"},
    {"value": f"{stats.get('avg_ats_score', 0):.0%}", "label": "Avg ATS Score"},
]
dark_hero(
    title="Pipeline Dashboard",
    gradient_word="Dashboard",
    subtitle="Real-time overview of your job search pipeline.",
    stats=hero_stats,
)

# ── KPI row ───────────────────────────────────────────────────────────────────
kpi_row([
    {"value": stats.get("total_jobs_found", 0),        "label": "Jobs Discovered",  "icon": "💼", "color": HT_COLORS["blue_500"]},
    {"value": stats.get("total_applications", 0),      "label": "Applications",     "icon": "📋", "color": HT_COLORS["violet_500"]},
    {"value": stats.get("applications_applied", 0),    "label": "Applied",          "icon": "📨", "color": HT_COLORS["info"]},
    {"value": stats.get("applications_interview", 0),  "label": "Interviews",       "icon": "🎯", "color": HT_COLORS["warning"]},
    {"value": stats.get("applications_offer", 0),      "label": "Offers",           "icon": "⭐", "color": HT_COLORS["success"]},
    {"value": f"{stats.get('avg_ats_score', 0):.0%}", "label": "Avg ATS Score",    "icon": "📈", "color": HT_COLORS["violet_500"]},
])

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ── Funnel + ATS ──────────────────────────────────────────────────────────────
section_header("Application Funnel & ATS Distribution")
col_l, col_r = st.columns(2)

with col_l:
    active = [d for d in funnel if d["count"] > 0]
    if active:
        stages = [d["stage"].replace("_", " ").title() for d in active]
        counts = [d["count"] for d in active]
        fig = go.Figure(go.Funnel(
            y=stages, x=counts,
            textinfo="value+percent initial",
            marker=dict(color=HT_CHART_COLORS[:len(stages)]),
            connector=dict(line=dict(color=HT_COLORS["line"], width=1)),
        ))
        st.plotly_chart(style_plotly(fig, 300), use_container_width=True)
    else:
        info_box("No funnel data yet — applications will appear here as they're created.")

with col_r:
    if ats_data:
        labels = [d["range_label"] for d in ats_data]
        counts = [d["count"] for d in ats_data]
        fig = go.Figure(go.Bar(
            x=labels, y=counts,
            marker_color=["#DC2626", "#D97706", "#D97706", "#059669", "#059669"],
            text=counts, textposition="outside",
            hovertemplate="%{x}: %{y} applications<extra></extra>",
        ))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style_plotly(fig, 300), use_container_width=True)
    else:
        info_box("No ATS score data yet.")

# ── Timeline ──────────────────────────────────────────────────────────────────
section_header("Daily Activity", "last 30 days")
if timeline:
    dates = [d["date"] for d in timeline]
    fig = go.Figure()
    series = [
        ("Jobs Found",    [d.get("jobs_found", 0) for d in timeline],              HT_COLORS["blue_500"]),
        ("Apps Created",  [d.get("applications_created", 0) for d in timeline],    HT_COLORS["violet_500"]),
        ("Applied",       [d.get("applications_applied", 0) for d in timeline],    HT_COLORS["success"]),
    ]
    for name, vals, color in series:
        fig.add_trace(go.Scatter(
            x=dates, y=vals, name=name,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=4),
            fill="tozeroy",
            fillcolor=color.replace("#", "rgba(").rstrip(")") + ",0.05)" if color.startswith("#") else color,
        ))
    st.plotly_chart(style_plotly(fig, 260), use_container_width=True)
else:
    info_box("No timeline data yet.")

# ── Status donut + Missing skills ─────────────────────────────────────────────
section_header("Status Breakdown & Skill Gaps")
col_a, col_b = st.columns(2)

with col_a:
    by_status: dict = dash.get("by_status", {})
    if by_status:
        labels = [k.replace("_", " ").title() for k in by_status]
        values = list(by_status.values())
        colors = [HT_STATUS.get(k, {}).get("color", "#64748B") for k in by_status]
        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.52,
            marker=dict(colors=colors),
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        st.plotly_chart(style_plotly(fig, 280), use_container_width=True)
    else:
        info_box("No application data yet.")

with col_b:
    missing = dash.get("top_missing_skills", [])
    if missing:
        skill_names  = [s.get("skill", "") for s in missing[:10]]
        skill_counts = [s.get("count", 0) for s in missing[:10]]
        fig = go.Figure(go.Bar(
            x=skill_counts, y=skill_names,
            orientation="h",
            marker=dict(
                color=HT_COLORS["error"],
                opacity=0.85,
                line=dict(color="white", width=1),
            ),
            text=skill_counts, textposition="outside",
        ))
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_plotly(fig, 280), use_container_width=True)

        # Skill gap chips
        st.markdown(
            skill_tags_html(skill_names, missing=skill_names),
            unsafe_allow_html=True,
        )
    else:
        info_box("Run skill gap analyses on your applications to see missing skills here.")
