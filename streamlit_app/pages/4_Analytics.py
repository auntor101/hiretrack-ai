"""Analytics page — deep-dive charts and LLM usage.
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
    kpi_row, style_plotly, info_box,
    HT_COLORS, HT_CHART_COLORS,
)

st.set_page_config(
    page_title="Analytics · HireTrack AI",
    page_icon="📈",
    layout="wide",
)
inject_global_css()
page_header("Analytics", "Deep-dive into your job search performance metrics.")

# ── Data ──────────────────────────────────────────────────────────────────────
stats    = api_get("/analytics/dashboard") or {}
funnel   = api_get("/analytics/funnel") or []
ats_data = api_get("/analytics/ats-scores") or []
timeline = api_get("/analytics/timeline") or []
llm_data = api_get("/analytics/llm-usage") or []

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_cost = stats.get("total_llm_cost_usd", 0) or 0
kpi_row([
    {"value": stats.get("total_jobs_found", 0),     "label": "Total Jobs",       "icon": "💼", "color": HT_COLORS["blue_500"]},
    {"value": stats.get("total_applications", 0),   "label": "Applications",     "icon": "📋", "color": HT_COLORS["violet_500"]},
    {"value": f"{stats.get('avg_ats_score', 0):.1%}", "label": "Avg ATS Score",  "icon": "📈", "color": HT_COLORS["warning"]},
    {"value": f"${total_cost:.4f}",                  "label": "LLM Cost (USD)",   "icon": "💰", "color": HT_COLORS["success"]},
])

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ── Funnel + ATS ──────────────────────────────────────────────────────────────
section_header("Application Funnel & ATS Distribution")
col1, col2 = st.columns(2)

with col1:
    active = [d for d in funnel if d["count"] > 0]
    if active:
        fig = go.Figure(go.Funnel(
            y=[d["stage"].replace("_", " ").title() for d in active],
            x=[d["count"] for d in active],
            textinfo="value+percent initial",
            marker=dict(color=HT_CHART_COLORS[:len(active)]),
            connector=dict(line=dict(color=HT_COLORS["line"], width=1)),
        ))
        st.plotly_chart(style_plotly(fig, 320), use_container_width=True)
    else:
        info_box("No funnel data yet.")

with col2:
    if ats_data:
        fig = go.Figure(go.Bar(
            x=[d["range_label"] for d in ats_data],
            y=[d["count"] for d in ats_data],
            marker=dict(
                color=["#DC2626", "#D97706", "#D97706", "#059669", "#059669"],
                line=dict(color="white", width=1),
            ),
            text=[d["count"] for d in ats_data],
            textposition="outside",
        ))
        st.plotly_chart(style_plotly(fig, 320), use_container_width=True)
    else:
        info_box("No ATS data yet.")

# ── Timeline ──────────────────────────────────────────────────────────────────
section_header("Daily Activity Timeline")
if timeline:
    dates = [d["date"] for d in timeline]
    fig   = go.Figure()
    for name, key, color in [
        ("Jobs Found",   "jobs_found",            HT_COLORS["blue_500"]),
        ("Apps Created", "applications_created",  HT_COLORS["violet_500"]),
        ("Applied",      "applications_applied",  HT_COLORS["success"]),
    ]:
        fig.add_trace(go.Scatter(
            x=dates, y=[d.get(key, 0) for d in timeline],
            name=name, mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=4),
        ))
    st.plotly_chart(style_plotly(fig, 280), use_container_width=True)
else:
    info_box("No timeline data yet.")

# ── LLM Usage ─────────────────────────────────────────────────────────────────
section_header("LLM Usage & Cost")
if llm_data:
    import pandas as pd

    df = pd.DataFrame(llm_data)
    df = df.rename(columns={
        "provider":       "Provider",
        "model":          "Model",
        "total_requests": "Requests",
        "total_tokens":   "Total Tokens",
        "total_cost_usd": "Cost (USD)",
        "avg_latency_ms": "Avg Latency",
    })
    if "Cost (USD)" in df.columns:
        df["Cost (USD)"] = df["Cost (USD)"].map("${:.6f}".format)
    if "Total Tokens" in df.columns:
        df["Total Tokens"] = df["Total Tokens"].map("{:,}".format)
    if "Avg Latency" in df.columns:
        df["Avg Latency"] = df["Avg Latency"].map("{:.0f} ms".format)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if len(llm_data) > 1:
        fig = go.Figure(go.Bar(
            x=[d.get("provider", "") for d in llm_data],
            y=[float(d.get("total_cost_usd", 0)) for d in llm_data],
            marker_color=HT_COLORS["blue_500"],
            text=[f"${float(d.get('total_cost_usd',0)):.6f}" for d in llm_data],
            textposition="outside",
        ))
        st.plotly_chart(style_plotly(fig, 220), use_container_width=True)
else:
    info_box("No LLM usage recorded yet. Generate cover letters or run job analysis to see usage here.")
