"""Dashboard page -- pipeline overview with KPIs and charts."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st
from utils import api_get, inject_global_css

st.set_page_config(
    page_title="Dashboard \u00b7 AutoApply AI",
    page_icon="\U0001f4cb",
    layout="wide",
)
inject_global_css()

st.markdown('<div class="page-title">\U0001f4cb Pipeline Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Real-time overview of your job search pipeline</div>',
    unsafe_allow_html=True,
)

# ── Data ─────────────────────────────────────────────────────────────────────
stats = api_get("/analytics/dashboard") or {}
dash = api_get("/dashboard/stats") or {}
funnel_data = api_get("/analytics/funnel") or []
ats_data = api_get("/analytics/ats-scores") or []
timeline_data = api_get("/analytics/timeline") or []

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, stats.get("total_jobs_found", 0), "Jobs Discovered", "#0A66C2"),
    (k2, stats.get("total_applications", 0), "Applications", "#06B6D4"),
    (k3, stats.get("applications_applied", 0), "Applied", "#3B82F6"),
    (k4, stats.get("applications_interview", 0), "Interviews", "#10B981"),
    (k5, stats.get("applications_offer", 0), "Offers", "#22C55E"),
    (k6, f"{stats.get('avg_ats_score', 0):.0%}", "Avg ATS Score", "#8B5CF6"),
]
for col, value, label, accent in kpis:
    col.markdown(
        f"""<div class="kpi-card" style="border-top-color:{accent}">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Funnel + ATS Distribution ─────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<div class="section-title">Application Funnel</div>', unsafe_allow_html=True)
    active = [d for d in funnel_data if d["count"] > 0]
    if active:
        stages = [d["stage"].replace("_", " ").title() for d in active]
        counts = [d["count"] for d in active]
        palette = [
            "#0A66C2", "#06B6D4", "#3B82F6", "#6366F1",
            "#8B5CF6", "#10B981", "#22C55E", "#EF4444", "#9CA3AF",
        ]
        fig = go.Figure(go.Funnel(
            y=stages,
            x=counts,
            textinfo="value+percent initial",
            marker=dict(color=palette[: len(stages)]),
            connector=dict(line=dict(color="#E5E7EB", width=1)),
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif", size=13),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No funnel data yet.")

with col_r:
    st.markdown('<div class="section-title">ATS Score Distribution</div>', unsafe_allow_html=True)
    if ats_data:
        labels = [d["range_label"] for d in ats_data]
        counts = [d["count"] for d in ats_data]
        bar_colors = ["#EF4444", "#F97316", "#F59E0B", "#22C55E", "#16A34A"]
        fig = go.Figure(go.Bar(
            x=labels,
            y=counts,
            marker_color=bar_colors,
            text=counts,
            textposition="outside",
            hovertemplate="%{x}: %{y} applications<extra></extra>",
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="ATS Score Range", gridcolor="#F3F4F6"),
            yaxis=dict(title="Applications", gridcolor="#F3F4F6"),
            font=dict(family="sans-serif", size=13),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No ATS score data yet.")

# ── Row 2: Timeline ───────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title">Daily Activity (Last 30 Days)</div>',
    unsafe_allow_html=True,
)
if timeline_data:
    dates = [d["date"] for d in timeline_data]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=[d.get("jobs_found", 0) for d in timeline_data],
        name="Jobs Found",
        mode="lines+markers",
        line=dict(color="#0A66C2", width=2),
        fill="tozeroy",
        fillcolor="rgba(10,102,194,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=[d.get("applications_created", 0) for d in timeline_data],
        name="Apps Created",
        mode="lines+markers",
        line=dict(color="#06B6D4", width=2),
        fill="tozeroy",
        fillcolor="rgba(6,182,212,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=[d.get("applications_applied", 0) for d in timeline_data],
        name="Applied",
        mode="lines+markers",
        line=dict(color="#22C55E", width=2),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#F3F4F6"),
        yaxis=dict(gridcolor="#F3F4F6"),
        legend=dict(orientation="h", y=1.1),
        font=dict(family="sans-serif", size=13),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No timeline data yet -- applications will appear here as they are created.")

# ── Row 3: Status donut + Missing Skills ───────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-title">Status Breakdown</div>', unsafe_allow_html=True)
    by_status: dict = dash.get("by_status", {})
    if by_status:
        labels = [k.replace("_", " ").title() for k in by_status]
        values = list(by_status.values())
        palette2 = ["#0A66C2", "#F59E0B", "#06B6D4", "#10B981", "#22C55E", "#EF4444", "#9CA3AF"]
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=palette2),
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(family="sans-serif", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No application data yet.")

with col_b:
    st.markdown('<div class="section-title">Top Missing Skills</div>', unsafe_allow_html=True)
    missing = dash.get("top_missing_skills", [])
    if missing:
        skill_names = [s.get("skill", "") for s in missing[:10]]
        skill_counts = [s.get("count", 0) for s in missing[:10]]
        fig = go.Figure(go.Bar(
            x=skill_counts,
            y=skill_names,
            orientation="h",
            marker_color="#0A66C2",
            text=skill_counts,
            textposition="outside",
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed"),
            xaxis=dict(gridcolor="#F3F4F6"),
            font=dict(family="sans-serif", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            '<div class="info-box">Run skill gap analyses on applications to surface '
            "missing skills here.</div>",
            unsafe_allow_html=True,
        )
