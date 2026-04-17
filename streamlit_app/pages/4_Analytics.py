"""Analytics page -- deep-dive charts and LLM usage."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st
from utils import api_get, inject_global_css

st.set_page_config(
    page_title="Analytics \u00b7 AutoApply AI",
    page_icon="\U0001f4c8",
    layout="wide",
)
inject_global_css()

st.markdown('<div class="page-title">\U0001f4c8 Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Deep-dive into your job search performance metrics</div>',
    unsafe_allow_html=True,
)

# ── Data ──────────────────────────────────────────────────────────────────────
stats = api_get("/analytics/dashboard") or {}
funnel_data = api_get("/analytics/funnel") or []
ats_data = api_get("/analytics/ats-scores") or []
timeline_data = api_get("/analytics/timeline") or []
llm_data = api_get("/analytics/llm-usage") or []

# ── Summary metrics ────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
total_cost = stats.get("total_llm_cost_usd", 0) or 0
metrics_row = [
    (m1, stats.get("total_jobs_found", 0), "Total Jobs", "#0A66C2"),
    (m2, stats.get("total_applications", 0), "Total Applications", "#06B6D4"),
    (m3, f"{stats.get('avg_ats_score', 0):.1%}", "Avg ATS Score", "#8B5CF6"),
    (m4, f"${total_cost:.4f}", "LLM Cost (USD)", "#F59E0B"),
]
for col, val, label, color in metrics_row:
    col.markdown(
        f"""<div class="kpi-card" style="border-top-color:{color}">
            <div class="kpi-value" style="font-size:28px">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Funnel + ATS ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Application Funnel</div>', unsafe_allow_html=True)
    active = [d for d in funnel_data if d["count"] > 0]
    if active:
        stage_labels = [d["stage"].replace("_", " ").title() for d in active]
        stage_vals = [d["count"] for d in active]
        # Funnel chart
        fig = go.Figure(go.Funnel(
            y=stage_labels,
            x=stage_vals,
            textinfo="value+percent initial",
            marker=dict(color=[
                "#0A66C2", "#06B6D4", "#3B82F6", "#6366F1",
                "#8B5CF6", "#10B981", "#22C55E", "#EF4444", "#9CA3AF",
            ][: len(active)]),
            connector=dict(line=dict(color="#E5E7EB", width=1)),
        ))
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif", size=13),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No funnel data yet.")

with col2:
    st.markdown('<div class="section-title">ATS Score Distribution</div>', unsafe_allow_html=True)
    if ats_data:
        ats_labels = [d["range_label"] for d in ats_data]
        ats_counts = [d["count"] for d in ats_data]
        fig = go.Figure(go.Bar(
            x=ats_labels,
            y=ats_counts,
            marker=dict(
                color=["#EF4444", "#F97316", "#F59E0B", "#22C55E", "#16A34A"],
                line=dict(color="white", width=1),
            ),
            text=ats_counts,
            textposition="outside",
            hovertemplate="Score %{x}: %{y} apps<extra></extra>",
        ))
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="ATS Score %", gridcolor="#F3F4F6"),
            yaxis=dict(title="Applications", gridcolor="#F3F4F6"),
            font=dict(family="sans-serif", size=13),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No ATS data yet.")

# ── Timeline ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Daily Activity Timeline</div>', unsafe_allow_html=True)
if timeline_data:
    dates = [d["date"] for d in timeline_data]
    fig = go.Figure()
    series = [
        ("Jobs Found", [d.get("jobs_found", 0) for d in timeline_data], "#0A66C2"),
        ("Apps Created", [d.get("applications_created", 0) for d in timeline_data], "#06B6D4"),
        ("Applied", [d.get("applications_applied", 0) for d in timeline_data], "#22C55E"),
    ]
    for name, values, color in series:
        fig.add_trace(go.Scatter(
            x=dates, y=values, name=name,
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=5),
        ))
    fig.update_layout(
        height=280, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.12),
        xaxis=dict(gridcolor="#F3F4F6"),
        yaxis=dict(gridcolor="#F3F4F6"),
        font=dict(family="sans-serif", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No timeline data yet.")

# ── LLM Usage ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title">LLM Usage &amp; Cost Breakdown</div>',
    unsafe_allow_html=True,
)
if llm_data:
    import pandas as pd

    df = pd.DataFrame(llm_data)
    rename_map = {
        "provider": "Provider",
        "model": "Model",
        "total_requests": "Requests",
        "total_tokens": "Total Tokens",
        "total_cost_usd": "Cost (USD)",
        "avg_latency_ms": "Avg Latency (ms)",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    if "Cost (USD)" in df.columns:
        df["Cost (USD)"] = df["Cost (USD)"].map("${:.6f}".format)
    if "Total Tokens" in df.columns:
        df["Total Tokens"] = df["Total Tokens"].map("{:,}".format)
    if "Avg Latency (ms)" in df.columns:
        df["Avg Latency (ms)"] = df["Avg Latency (ms)"].map("{:.0f} ms".format)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Cost bar chart
    if len(llm_data) > 1:
        providers = [d.get("provider", "") for d in llm_data]
        costs = [float(d.get("total_cost_usd", 0)) for d in llm_data]
        fig = go.Figure(go.Bar(
            x=providers,
            y=costs,
            marker_color="#0A66C2",
            text=[f"${c:.6f}" for c in costs],
            textposition="outside",
        ))
        fig.update_layout(
            height=220, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="Cost USD", gridcolor="#F3F4F6"),
            font=dict(family="sans-serif", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown(
        '<div class="info-box">No LLM usage recorded yet. Generate cover letters or '
        "run job analysis to see usage here.</div>",
        unsafe_allow_html=True,
    )
