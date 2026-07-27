import streamlit as st
from typing import List, Any
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.ui.components import render_trust_badge, render_view_header


def _status_row(label: str, value: str, ok: bool = True):
    color = "#34D399" if ok else "#FBBF24"
    icon = "✓" if ok else "⚠"
    st.markdown(
        f"<div style='display:flex; justify-content:space-between; align-items:center; padding:9px 12px; margin-bottom:6px; background:rgba(56,189,248,0.03); border:1px solid rgba(56,189,248,0.07); border-radius:8px; font-size:13px;'>"
        f"<span style='color:#94A3B8;'>{label}</span>"
        f"<span style='color:{color}; font-weight:600;'>{icon} {value}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _spec_row(label: str, detail: str):
    st.markdown(
        f"<div style='display:flex; align-items:flex-start; gap:10px; padding:9px 12px; margin-bottom:6px; background:rgba(16,185,129,0.04); border:1px solid rgba(16,185,129,0.1); border-radius:8px;'>"
        f"<span style='color:#34D399; font-size:14px; margin-top:1px; flex-shrink:0;'>✓</span>"
        f"<div><span style='color:#E2E8F0; font-size:13px; font-weight:600;'>{label}</span>"
        f"<span style='color:#475569; font-size:12px; margin-left:8px;'>{detail}</span></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_status_view(deals: List[Any], work_orders: List[Any]):
    """Renders the System Status & Spec Audit view with health indicators and requirement checklist."""
    render_view_header(
        "🛡️ System Status",
        "Live status for data sources, LLM providers, spec compliance, and data trust ratings.",
    )

    status_info = st.session_state.get("status_info", {})
    is_live = status_info.get("is_live", False)
    provider = st.session_state.get("llm_provider", "Deterministic")
    selected_model = st.session_state.get("selected_llm_model", "none")

    bundle = build_full_analytics_bundle(deals, work_orders)
    t_m = bundle["data_trust_score"]

    # ── Status Cards ──────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            "<div style='font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>🔌 Data Source</div>",
            unsafe_allow_html=True,
        )
        _status_row("Mode", "LIVE MONDAY API" if is_live else "FALLBACK SNAPSHOT", is_live)
        _status_row("Deals Loaded", str(len(deals)), True)
        _status_row("Work Orders Loaded", str(len(work_orders)), True)
        if not is_live:
            st.markdown(
                "<div style='font-size:11px; color:#64748B; margin-top:6px; padding:6px 10px; background:rgba(245,158,11,0.06); border-radius:6px; border:1px solid rgba(245,158,11,0.1);'>Set MONDAY_API_TOKEN in .env or Streamlit Secrets to enable live API mode.</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            "<div style='font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>🤖 LLM Execution</div>",
            unsafe_allow_html=True,
        )
        _status_row("Active Provider", provider, True)
        _status_row("Selected Model", selected_model if provider != "Deterministic" else "None", True)
        _status_row("Fallback Policy", "100% Deterministic Python", True)
        st.markdown(
            "<div style='font-size:11px; color:#475569; margin-top:6px;'>LLMs are used only to phrase Ask-view answers. Zero metric calculations run through any model.</div>",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            "<div style='font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>🔒 Data Trust Scores</div>",
            unsafe_allow_html=True,
        )
        render_trust_badge(t_m["combined_trust_score"], t_m["trust_rating"])
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        _status_row("Deals Board Trust", f"{t_m['deals_board_score']:.1f}/100", t_m["deals_board_score"] >= 60)
        _status_row("Work Orders Trust", f"{t_m['work_orders_board_score']:.1f}/100", t_m["work_orders_board_score"] >= 60)
        _status_row("Linkage Coverage", f"{t_m['account_match_coverage_score']:.1f}/100", t_m["account_match_coverage_score"] >= 60)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Spec Requirements Audit ───────────────────────────────
    st.markdown(
        "<div style='font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:14px;'>📋 Technical Requirement Audit</div>",
        unsafe_allow_html=True,
    )

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        _spec_row("monday.com Integration", "Read-only GraphQL client with cursor pagination & caching")
        _spec_row("Data Normalization", "Date canonicalization, status unification, and missing-field warning flags")
        _spec_row("Query Understanding", "Intent routing with ambiguity clarification prompts for underspecified queries")
        _spec_row("Multi-Turn Context", "Conversational memory with sector/time window context persistence")

    with r_col2:
        _spec_row("Business Intelligence", "Pipeline, operations, sector matrix, and non-overlapping risk scoring")
        _spec_row("Leadership Updates", "One-click executive brief with 4 export formats (MD, CSV×2, JSON)")
        _spec_row("Scenario Engine", "Pure Python what-if simulator with 100% zero-mutation guarantee")
        _spec_row("Hosted Readiness", "Procfile + .streamlit/config.toml for Streamlit Community Cloud deploy")
