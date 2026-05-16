"""
HireTrack AI — Streamlit component library.
Drop-in companion to utils.py that upgrades the visual layer to match
the HireTrack AI design system (frontend/src/theme.ts / colors_and_type.css).

Usage in each page (replace the utils imports):
    from ht_components import (
        inject_global_css, page_header, kpi_row,
        status_chip_html, ats_chip_html, skill_tags_html,
        job_card_html, app_card_html, section_header,
        ai_callout, info_box, dark_hero, style_plotly,
        HT_COLORS, HT_STATUS,
    )

All existing utils.py helpers (api_get, api_post, api_put, etc.) remain
importable from utils.py as before — this file only adds/replaces the
visual layer.
"""
from __future__ import annotations

import html as _html
from typing import Any

import streamlit as st

# ── Brand token constants (mirror colors_and_type.css / theme.ts) ────────────

HT_COLORS = {
    "blue_500":   "#0A66C2",
    "blue_300":   "#378FE9",
    "blue_700":   "#004182",
    "violet_500": "#7C3AED",
    "violet_300": "#A78BFA",
    "success":    "#059669",
    "warning":    "#D97706",
    "info":       "#0EA5E9",
    "error":      "#DC2626",
    "ink":        "#0F172A",
    "ink_muted":  "#64748B",
    "canvas":     "#F0F4FA",
    "paper":      "#FFFFFF",
    "line":       "#E2E8F0",
    "line_soft":  "#F1F5F9",
    "table_head": "#F8FAFC",
    "night_900":  "#0C1526",
    "night_800":  "#0F172A",
    "night_700":  "#1A1F35",
    "night_aurora": "#1A1035",
}

# Status colors — exact values from theme.ts statusColors
HT_STATUS: dict[str, dict[str, str]] = {
    "queued":        {"color": "#64748B", "bg": "rgba(100,116,139,0.10)", "label": "Queued"},
    "pending_review":{"color": "#D97706", "bg": "rgba(217,119,6,0.10)",   "label": "Pending Review"},
    "approved":      {"color": "#0A66C2", "bg": "rgba(10,102,194,0.10)",  "label": "Approved"},
    "applying":      {"color": "#7C3AED", "bg": "rgba(124,58,237,0.10)",  "label": "Applying"},
    "applied":       {"color": "#0A66C2", "bg": "rgba(10,102,194,0.10)",  "label": "Applied"},
    "interview":     {"color": "#7C3AED", "bg": "rgba(124,58,237,0.10)",  "label": "Interview"},
    "offer":         {"color": "#059669", "bg": "rgba(5,150,105,0.10)",   "label": "Offer"},
    "rejected":      {"color": "#DC2626", "bg": "rgba(220,38,38,0.10)",   "label": "Rejected"},
    "withdrawn":     {"color": "#64748B", "bg": "rgba(100,116,139,0.10)", "label": "Withdrawn"},
    "failed":        {"color": "#DC2626", "bg": "rgba(220,38,38,0.10)",   "label": "Failed"},
}

# Backward-compatible flat map (replaces utils.STATUS_COLORS)
STATUS_COLORS: dict[str, str] = {k: v["color"] for k, v in HT_STATUS.items()}

# Chart color sequence — matches brand palette order
HT_CHART_COLORS = [
    "#0A66C2", "#7C3AED", "#059669", "#D97706",
    "#0EA5E9", "#A78BFA", "#DC2626", "#64748B",
]

EXP_COLORS: dict[str, str] = {
    "entry":  "#059669",
    "junior": "#059669",
    "mid":    "#0A66C2",
    "senior": "#7C3AED",
    "lead":   "#D97706",
    "staff":  "#DC2626",
}


# ── Global CSS ────────────────────────────────────────────────────────────────

def inject_global_css() -> None:
    """
    Inject HireTrack AI brand CSS into the page.
    Call once at the top of every page, after st.set_page_config().
    Replaces utils.inject_global_css().
    """
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

        <style>
        /* ── Base ─────────────────────────────────────────────────── */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        #MainMenu  { visibility: hidden; }
        footer     { visibility: hidden; }
        header     { visibility: hidden; }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }

        /* ── Page header ────────────────────────────────────────────── */
        .ht-page-title {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #0F172A;
            line-height: 1.1;
            margin: 0 0 4px;
        }
        .ht-page-subtitle {
            font-size: 14px;
            color: #64748B;
            margin-bottom: 24px;
            font-weight: 400;
        }

        /* ── Section header ─────────────────────────────────────────── */
        .ht-section {
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.01em;
            margin: 28px 0 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #E2E8F0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .ht-section-sub {
            font-size: 12px;
            font-weight: 400;
            color: #64748B;
            margin-left: 4px;
        }

        /* ── KPI cards ──────────────────────────────────────────────── */
        .ht-kpi {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.05), 0 2px 8px rgba(15,23,42,0.04);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            transition: box-shadow 200ms ease, transform 200ms ease;
        }
        .ht-kpi:hover {
            box-shadow: 0 0 0 1px rgba(15,23,42,0.07), 0 10px 28px rgba(15,23,42,0.09);
            transform: translateY(-2px);
        }
        .ht-kpi-meta {
            font-size: 12px;
            font-weight: 500;
            color: #64748B;
            margin-bottom: 8px;
        }
        .ht-kpi-value {
            font-size: 36px;
            font-weight: 800;
            line-height: 1;
        }
        .ht-kpi-icon {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex-shrink: 0;
        }

        /* ── Status chips ────────────────────────────────────────────── */
        .ht-chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            height: 24px;
            padding: 0 10px;
            border-radius: 8px;
            font-size: 11.5px;
            font-weight: 600;
            white-space: nowrap;
            letter-spacing: 0.01em;
        }

        /* ── Job cards ───────────────────────────────────────────────── */
        .ht-job {
            background: #FFFFFF;
            border-radius: 14px;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.05), 0 2px 8px rgba(15,23,42,0.04);
            margin-bottom: 14px;
            overflow: hidden;
            transition: box-shadow 200ms ease, transform 200ms ease;
        }
        .ht-job:hover {
            box-shadow: 0 0 0 1px rgba(15,23,42,0.07), 0 10px 28px rgba(15,23,42,0.09);
            transform: translateY(-2px);
        }
        .ht-job-body { padding: 20px 22px 14px; }
        .ht-job-title {
            font-size: 17px;
            font-weight: 700;
            color: #0A66C2;
            margin: 0 0 3px;
        }
        .ht-job-company {
            font-size: 14px;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 8px;
        }
        .ht-job-meta {
            font-size: 12.5px;
            color: #64748B;
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            align-items: center;
            margin-bottom: 10px;
        }
        .ht-job-salary {
            color: #059669;
            font-weight: 700;
        }
        .ht-job-footer {
            padding: 11px 22px;
            border-top: 1px solid #E2E8F0;
            background: rgba(10,102,194,0.015);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* ── Application cards ───────────────────────────────────────── */
        .ht-app {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.05), 0 2px 8px rgba(15,23,42,0.04);
            margin-bottom: 10px;
            border-left: 3px solid #E2E8F0;
            transition: box-shadow 180ms ease;
        }
        .ht-app:hover {
            box-shadow: 0 0 0 1px rgba(15,23,42,0.07), 0 8px 24px rgba(15,23,42,0.07);
        }
        .ht-app-title {
            font-size: 15px;
            font-weight: 700;
            color: #0F172A;
        }
        .ht-app-company {
            font-size: 13px;
            color: #64748B;
            margin-top: 2px;
        }

        /* ── AI callout ──────────────────────────────────────────────── */
        .ht-ai {
            background: linear-gradient(135deg,
                rgba(10,102,194,0.05) 0%,
                rgba(124,58,237,0.07) 100%);
            border: 1px solid rgba(124,58,237,0.15);
            border-radius: 14px;
            padding: 16px 18px;
            margin: 12px 0;
            font-size: 13.5px;
            line-height: 1.65;
            color: #0F172A;
        }
        .ht-ai-head {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #7C3AED;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* ── Info boxes ──────────────────────────────────────────────── */
        .ht-info {
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 13.5px;
            line-height: 1.6;
            margin: 8px 0;
        }
        .ht-info-info    { background: rgba(10,102,194,0.07); color: #004182;
                            border-left: 3px solid #0A66C2; }
        .ht-info-success { background: rgba(5,150,105,0.08); color: #065F46;
                            border-left: 3px solid #059669; }
        .ht-info-warning { background: rgba(217,119,6,0.09); color: #92400E;
                            border-left: 3px solid #D97706; }
        .ht-info-error   { background: rgba(220,38,38,0.08); color: #7F1D1D;
                            border-left: 3px solid #DC2626; }

        /* ── Dark hero banner ────────────────────────────────────────── */
        .ht-hero {
            background: linear-gradient(135deg, #0C1526 0%, #0F172A 45%, #1A1035 100%);
            border-radius: 20px;
            padding: 40px 44px;
            color: white;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }
        .ht-hero-title {
            font-size: 38px;
            font-weight: 800;
            letter-spacing: -0.025em;
            line-height: 1.1;
            margin: 0 0 12px;
        }
        .ht-hero-gradient {
            background: linear-gradient(90deg, #378FE9, #A78BFA);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .ht-hero-sub {
            font-size: 15px;
            color: rgba(255,255,255,0.65);
            line-height: 1.6;
            max-width: 520px;
            margin-bottom: 0;
        }
        .ht-hero-stat { text-align: center; }
        .ht-hero-stat-val {
            font-size: 28px;
            font-weight: 800;
            color: white;
            line-height: 1;
        }
        .ht-hero-stat-lbl {
            font-size: 11px;
            color: rgba(255,255,255,0.55);
            margin-top: 4px;
            letter-spacing: 0.02em;
        }
        .ht-hero-divider {
            width: 1px;
            background: rgba(255,255,255,0.12);
            height: 36px;
            margin: auto 0;
        }

        /* ── Skill tags ──────────────────────────────────────────────── */
        .ht-skill-have {
            display: inline-flex; align-items: center; gap: 3px;
            background: rgba(5,150,105,0.08);
            color: #059669;
            border: 1px solid rgba(5,150,105,0.25);
            padding: 2px 9px;
            border-radius: 7px;
            font-size: 11.5px;
            font-weight: 600;
            margin: 2px;
        }
        .ht-skill-missing {
            display: inline-flex; align-items: center; gap: 3px;
            background: rgba(220,38,38,0.07);
            color: #DC2626;
            border: 1px solid rgba(220,38,38,0.22);
            padding: 2px 9px;
            border-radius: 7px;
            font-size: 11.5px;
            font-weight: 600;
            margin: 2px;
        }
        .ht-skill-neutral {
            display: inline-block;
            background: #F1F5F9;
            color: #334155;
            border: 1px solid #E2E8F0;
            padding: 2px 9px;
            border-radius: 7px;
            font-size: 11.5px;
            font-weight: 500;
            margin: 2px;
        }

        /* ── Remote / job-type badges ────────────────────────────────── */
        .ht-remote {
            background: rgba(5,150,105,0.10);
            color: #059669;
            padding: 2px 9px;
            border-radius: 7px;
            font-size: 11.5px;
            font-weight: 600;
        }
        .ht-onsite {
            background: #F1F5F9;
            color: #64748B;
            padding: 2px 9px;
            border-radius: 7px;
            font-size: 11.5px;
            font-weight: 500;
        }
        .ht-jtype {
            background: #F1F5F9;
            color: #475569;
            padding: 2px 9px;
            border-radius: 7px;
            font-size: 11.5px;
            font-weight: 500;
        }

        /* ── Streamlit widget overrides ──────────────────────────────── */
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: transparent;
            border-bottom: 1px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            font-size: 13.5px;
        }
        /* Primary button */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0A66C2 0%, #1570E0 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 180ms cubic-bezier(0.4,0,0.2,1) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #004182 0%, #0A66C2 100%) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(10,102,194,0.35) !important;
        }
        /* Secondary button */
        .stButton > button[kind="secondary"] {
            border-radius: 10px !important;
            font-weight: 600 !important;
            border-color: #E2E8F0 !important;
        }
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > div > textarea {
            border-radius: 10px !important;
            border-color: #E2E8F0 !important;
            transition: box-shadow 150ms ease !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            box-shadow: 0 0 0 3px rgba(10,102,194,0.15) !important;
            border-color: #0A66C2 !important;
        }
        /* Slider accent */
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background-color: #0A66C2 !important;
        }
        /* Metric (st.metric) */
        [data-testid="stMetric"] {
            background: white;
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.05), 0 2px 8px rgba(15,23,42,0.04);
        }
        [data-testid="stMetricValue"] {
            font-size: 36px !important;
            font-weight: 800 !important;
            color: #0F172A !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 12px !important;
            font-weight: 500 !important;
            color: #64748B !important;
        }
        /* DataFrame */
        [data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.05);
        }
        /* Expander */
        .streamlit-expanderHeader {
            font-weight: 600 !important;
            font-size: 13.5px !important;
            border-radius: 10px !important;
        }
        .streamlit-expanderContent {
            border-left: none !important;
            padding-top: 12px !important;
        }
        /* Progress bar */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #0A66C2, #378FE9) !important;
            border-radius: 999px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Component helpers ─────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "") -> None:
    """Branded page title + subtitle."""
    safe_title    = _html.escape(title)
    safe_subtitle = _html.escape(subtitle) if subtitle else ""
    st.markdown(
        f'<div class="ht-page-title">{safe_title}</div>'
        + (f'<div class="ht-page-subtitle">{safe_subtitle}</div>' if safe_subtitle else ""),
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    """Lightweight section divider with optional sub-label."""
    safe_t = _html.escape(title)
    safe_s = (
        f'<span class="ht-section-sub">· {_html.escape(subtitle)}</span>'
        if subtitle else ""
    )
    st.markdown(
        f'<div class="ht-section">{safe_t}{safe_s}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(
    container: Any,
    value: Any,
    label: str,
    icon: str,
    color: str,
) -> None:
    """
    Icon-tile KPI card rendered inside a Streamlit column.
    icon is a single emoji or short Unicode glyph (no Material Symbols here).
    """
    bg = _alpha_bg(color, 0.08)
    safe_label = _html.escape(label)
    container.markdown(
        f"""<div class="ht-kpi">
            <div>
                <div class="ht-kpi-meta">{safe_label}</div>
                <div class="ht-kpi-value" style="color:{color}">{value}</div>
            </div>
            <div class="ht-kpi-icon" style="background:{bg};color:{color}">{icon}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def kpi_row(kpis: list[dict]) -> None:
    """
    Render a row of KPI cards from a list of dicts:
        [{"value": 42, "label": "Applications", "icon": "📋", "color": "#0A66C2"}, ...]
    """
    cols = st.columns(len(kpis))
    for col, k in zip(cols, kpis):
        kpi_card(col, k["value"], k["label"], k["icon"], k["color"])


# ── HTML badge / chip helpers ─────────────────────────────────────────────────

def status_chip_html(status: str) -> str:
    """10%-alpha status chip — exact recipe from the design system."""
    s = HT_STATUS.get(status, {"color": "#64748B", "bg": "rgba(100,116,139,0.10)", "label": status.replace("_", " ").title()})
    label = _html.escape(s["label"])
    return (
        f'<span class="ht-chip" '
        f'style="background:{s["bg"]};color:{s["color"]}">'
        f'{label}</span>'
    )


# Backward-compatible alias
def status_badge_html(status: str) -> str:
    return status_chip_html(status)


def ats_chip_html(score: float | None) -> str:
    """ATS score chip — green ≥75, amber ≥50, red <50."""
    if score is None:
        return '<span style="color:#64748B;font-size:12px;font-weight:500">—</span>'
    pct = round(score * 100)
    if pct >= 75:
        color, bg = "#059669", "rgba(5,150,105,0.10)"
    elif pct >= 50:
        color, bg = "#D97706", "rgba(217,119,6,0.10)"
    else:
        color, bg = "#DC2626", "rgba(220,38,38,0.10)"
    return (
        f'<span class="ht-chip" '
        f'style="background:{bg};color:{color};font-weight:700">{pct}%</span>'
    )


# Backward-compatible alias
def ats_badge_html(score: float | None) -> str:
    return ats_chip_html(score)


def exp_badge_html(level: str | None) -> str:
    if not level:
        return ""
    color = EXP_COLORS.get(level.lower(), "#64748B")
    bg    = _alpha_bg(color, 0.09)
    safe  = _html.escape(level.title())
    return (
        f'<span class="ht-chip" '
        f'style="background:{bg};color:{color};font-size:10.5px;letter-spacing:0.04em;'
        f'text-transform:uppercase">{safe}</span>'
    )


def skill_tags_html(
    skills: list[str],
    have: list[str] | None = None,
    missing: list[str] | None = None,
    limit: int = 8,
) -> str:
    """
    Render skill pills.
    - If have/missing lists are provided, green = matched, red = gap.
    - Otherwise renders neutral style.
    """
    have_set    = {s.lower() for s in (have or [])}
    missing_set = {s.lower() for s in (missing or [])}
    tags = []
    for s in skills[:limit]:
        safe = _html.escape(s)
        lo   = s.lower()
        if lo in have_set:
            tags.append(f'<span class="ht-skill-have">✓ {safe}</span>')
        elif lo in missing_set:
            tags.append(f'<span class="ht-skill-missing">+ {safe}</span>')
        else:
            tags.append(f'<span class="ht-skill-neutral">{safe}</span>')
    return "".join(tags)


# ── Card helpers ──────────────────────────────────────────────────────────────

def job_card_html(
    job: dict,
    match_score: int | None = None,
    applied: bool = False,
) -> str:
    """
    Full branded job card HTML.
    Use inside st.markdown(..., unsafe_allow_html=True).
    """
    title   = _html.escape(job.get("title", ""))
    company = _html.escape(job.get("company", ""))
    loc     = _html.escape(job.get("location", ""))
    salary  = _html.escape(job.get("salary_range", "") or "")
    jtype   = _html.escape(job.get("job_type", "").replace("_", "-"))
    remote  = job.get("remote", False)
    exp_lvl = job.get("experience_level", "")

    remote_html = (
        '<span class="ht-remote">Remote</span>'
        if remote
        else '<span class="ht-onsite">On-site</span>'
    )
    salary_html = (
        f'<span class="ht-job-salary">{salary}</span>' if salary else ""
    )
    score_html = (
        f'<span class="ht-chip" style="background:rgba(10,102,194,0.08);'
        f'color:#0A66C2;font-weight:700">{match_score}% match</span>'
        if match_score is not None else ""
    )
    applied_html = (
        '<span class="ht-chip" style="background:rgba(10,102,194,0.10);'
        'color:#0A66C2">Applied</span>'
        if applied else ""
    )

    skills_req  = (job.get("skills_required") or {}).get("required", [])
    skills_pref = (job.get("skills_required") or {}).get("preferred", [])
    skills_html = skill_tags_html(skills_req + skills_pref, limit=6)

    return f"""
    <div class="ht-job">
        <div class="ht-job-body">
            <div class="ht-job-title">{title}</div>
            <div class="ht-job-company">{company}</div>
            <div class="ht-job-meta">
                <span>📍 {loc}</span>
                {salary_html}
                {remote_html}
                {exp_badge_html(exp_lvl)}
                <span class="ht-jtype">{jtype}</span>
            </div>
            <div>{skills_html}</div>
        </div>
        <div class="ht-job-footer">
            {score_html}
            {applied_html}
        </div>
    </div>
    """


def app_card_html(app: dict, job: dict | None = None) -> str:
    """Branded application row card."""
    job        = job or {}
    title      = _html.escape(job.get("title", "Unknown Position"))
    company    = _html.escape(job.get("company", "Unknown Company"))
    status     = app.get("status", "queued")
    border_col = HT_STATUS.get(status, {}).get("color", "#E2E8F0")
    notes_html = ""
    if app.get("notes"):
        notes_html = (
            f'<div style="font-size:12.5px;color:#64748B;margin-top:8px;'
            f'font-style:italic;padding-top:8px;border-top:1px solid #F1F5F9">'
            f'📝 {_html.escape(str(app["notes"]))}</div>'
        )
    return f"""
    <div class="ht-app" style="border-left-color:{border_col}">
        <div style="display:flex;justify-content:space-between;
                    align-items:flex-start;flex-wrap:wrap;gap:8px">
            <div>
                <div class="ht-app-title">{title}</div>
                <div class="ht-app-company">🏢 {company}</div>
            </div>
            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                {status_chip_html(status)}
                {ats_chip_html(app.get("ats_score"))}
            </div>
        </div>
        {notes_html}
    </div>
    """


# ── Content blocks ────────────────────────────────────────────────────────────

def ai_callout(text: str, title: str = "AI Summary") -> None:
    """Violet-tinted AI content block."""
    safe_title = _html.escape(title)
    safe_text  = _html.escape(text)
    st.markdown(
        f"""<div class="ht-ai">
            <div class="ht-ai-head">✦ {safe_title}</div>
            {safe_text}
        </div>""",
        unsafe_allow_html=True,
    )


def info_box(text: str, kind: str = "info") -> None:
    """
    Contextual message box.
    kind: 'info' | 'success' | 'warning' | 'error'
    """
    safe  = _html.escape(text)
    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    icon  = icons.get(kind, "ℹ️")
    st.markdown(
        f'<div class="ht-info ht-info-{kind}">{icon} {safe}</div>',
        unsafe_allow_html=True,
    )


def dark_hero(
    title: str,
    gradient_word: str = "",
    subtitle: str = "",
    stats: list[dict] | None = None,
) -> None:
    """
    Full-width dark gradient hero banner.
    gradient_word — the word/phrase inside title that gets the brand gradient.
    stats — list of {"value": …, "label": …} shown as a stat row.

    Example:
        dark_hero(
            title="Your Job Search Command Center",
            gradient_word="Command Center",
            subtitle="AI-powered pipeline. Every application tracked.",
            stats=[{"value": 142, "label": "Applications"}, ...],
        )
    """
    safe_title    = _html.escape(title)
    safe_subtitle = _html.escape(subtitle) if subtitle else ""
    safe_grad     = _html.escape(gradient_word) if gradient_word else ""

    if gradient_word and gradient_word in title:
        display_title = safe_title.replace(
            safe_grad,
            f'<span class="ht-hero-gradient">{safe_grad}</span>',
        )
    else:
        display_title = safe_title

    stats_html = ""
    if stats:
        items = []
        for s in stats:
            val = _html.escape(str(s.get("value", "")))
            lbl = _html.escape(str(s.get("label", "")))
            items.append(
                f'<div class="ht-hero-stat">'
                f'<div class="ht-hero-stat-val">{val}</div>'
                f'<div class="ht-hero-stat-lbl">{lbl}</div>'
                f'</div>'
            )
        # join with thin vertical dividers
        inner = '<div class="ht-hero-divider"></div>'.join(items)
        stats_html = (
            f'<div style="display:flex;gap:28px;align-items:center;'
            f'margin-top:28px;padding-top:22px;'
            f'border-top:1px solid rgba(255,255,255,0.10)">{inner}</div>'
        )

    subtitle_html = (
        f'<div class="ht-hero-sub">{safe_subtitle}</div>' if safe_subtitle else ""
    )

    st.markdown(
        f"""<div class="ht-hero">
            <div class="ht-hero-title">{display_title}</div>
            {subtitle_html}
            {stats_html}
        </div>""",
        unsafe_allow_html=True,
    )


# ── Plotly layout helper ──────────────────────────────────────────────────────

def style_plotly(fig: Any, height: int = 300) -> Any:
    """
    Apply HireTrack brand styling to a plotly figure.
    Returns the figure for chaining.

    Usage:
        fig = go.Figure(...)
        st.plotly_chart(style_plotly(fig), use_container_width=True)
    """
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, 'Segoe UI', system-ui, sans-serif", size=12, color="#64748B"),
        legend=dict(
            orientation="h",
            y=1.1,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", tickfont=dict(size=11)),
    )
    return fig


# ── Internal helpers ──────────────────────────────────────────────────────────

def _alpha_bg(hex_color: str, alpha: float) -> str:
    """Convert a hex color to rgba() string for use as a background."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
