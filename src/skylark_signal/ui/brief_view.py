import streamlit as st
from typing import List, Any
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.ui.components import render_status_badge, render_trust_badge, render_view_header
from skylark_signal.reporting.export import (
    export_leadership_brief_markdown,
    export_attention_queue_csv,
    export_evidence_bundle_csv,
    export_analytics_snapshot_json,
)


def render_brief_view(deals: List[Any], work_orders: List[Any]):
    """Renders the Leadership Brief view as a board-ready executive memo with 4 one-click export formats."""
    render_view_header(
        "📄 Leadership Brief",
        "Board-ready executive briefing synthesized deterministically from live Deals and Work Orders boards.",
    )

    bundle = build_full_analytics_bundle(deals, work_orders)
    brief = bundle["leadership_brief"]
    t_m = bundle["data_trust_score"]

    # ── Brief Header ──────────────────────────────────────────
    b_col1, b_col2 = st.columns([3, 1])
    with b_col1:
        st.markdown(
            f"""
            <div style="margin-bottom:4px;">
                <span style="font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px;">Executive Briefing</span>
            </div>
            <div style="font-size:24px; font-weight:800; color:#F0F8FF; letter-spacing:-0.8px; margin-bottom:6px;">
                🦅 Skylark Signal Board Brief
            </div>
            <div style="font-size:12px; color:#475569;">
                Generated: <code style="color:#38BDF8;">{brief.get('timestamp', '')[:19].replace('T', ' ')} UTC</code>
                &nbsp;·&nbsp; Trust Score: <code style="color:#A5B4FC;">{t_m['combined_trust_score']:.1f}/100</code>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b_col2:
        st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
        render_status_badge(brief["overall_status"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Executive Pulse ───────────────────────────────────────
    st.markdown(
        f"""
        <div class="card-info">
            <div style="font-size:11px; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">
                💡 Executive Pulse — 2-Sentence Summary
            </div>
            <div style="font-size:15px; color:#BAE6FD; line-height:1.8;">
                {brief["executive_pulse"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Five Numbers ──────────────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin:20px 0 12px 0;'>📊 Five Numbers to Quote in Leadership Sync</div>",
        unsafe_allow_html=True,
    )
    quote_items = list(brief["five_numbers_to_quote"].items()) if isinstance(brief["five_numbers_to_quote"], dict) else []
    q_cols = st.columns(5)
    for idx, (lbl, val) in enumerate(quote_items[:5]):
        with q_cols[idx]:
            st.metric(label=lbl, value=str(val))

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Wins vs Risks ─────────────────────────────────────────
    w_col1, w_col2 = st.columns(2)

    with w_col1:
        wins_html = "".join(
            f'<div class="card-win" style="padding:14px 16px; margin-bottom:10px;">'
            f'<div style="font-size:13px; font-weight:600; color:#34D399;">{(win.get("title", "") if isinstance(win, dict) else str(win))}</div>'
            + (f'<div style="font-size:12px; color:#64748B; margin-top:4px;">{win.get("detail", "")}</div>' if isinstance(win, dict) and win.get("detail") else "")
            + "</div>"
            for win in brief["top_wins"]
        )
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:700; color:#34D399; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;">
                🎉 Commercial & Delivery Wins
            </div>
            {wins_html}
            """,
            unsafe_allow_html=True,
        )

    with w_col2:
        risks_html = "".join(
            f'<div class="card-risk" style="padding:14px 16px; margin-bottom:10px;">'
            f'<div style="font-size:13px; font-weight:600; color:#F87171;">{(risk.get("title", "") if isinstance(risk, dict) else str(risk))}</div>'
            + (f'<div style="font-size:12px; color:#64748B; margin-top:4px;">{risk.get("detail", "")}</div>' if isinstance(risk, dict) and risk.get("detail") else "")
            + "</div>"
            for risk in brief["top_risks"]
        )
        st.markdown(
            f"""
            <div style="font-size:12px; font-weight:700; color:#F87171; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;">
                🚨 Operational & Revenue Risks
            </div>
            {risks_html}
            """,
            unsafe_allow_html=True,
        )

    # ── Decisions & Actions ───────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    actions_html = "".join(
        f'<div style="display:flex; align-items:flex-start; gap:10px; padding:10px 14px; margin-bottom:8px; background:rgba(56,189,248,0.04); border:1px solid rgba(56,189,248,0.1); border-radius:10px;">'
        f'<span style="color:#38BDF8; font-size:14px; margin-top:1px;">→</span>'
        f'<span style="font-size:13px; color:#CBD5E1;">{act}</span>'
        f"</div>"
        for act in brief["decisions_required"]
    )
    st.markdown(
        f"""
        <div style="font-size:12px; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;">
            🎯 Leadership Decisions &amp; Action Items
        </div>
        {actions_html}
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── One-Click Exports ─────────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;'>📥 One-Click Executive Exports</div>",
        unsafe_allow_html=True,
    )

    e_col1, e_col2, e_col3, e_col4 = st.columns(4)

    with e_col1:
        st.download_button(
            label="📄 Brief (.md)",
            data=export_leadership_brief_markdown(bundle),
            file_name="leadership_brief.md",
            mime="text/markdown",
        )
    with e_col2:
        st.download_button(
            label="📊 Queue (.csv)",
            data=export_attention_queue_csv(bundle),
            file_name="attention_queue.csv",
            mime="text/csv",
        )
    with e_col3:
        st.download_button(
            label="🔍 Evidence (.csv)",
            data=export_evidence_bundle_csv(bundle),
            file_name="evidence_bundle.csv",
            mime="text/csv",
        )
    with e_col4:
        st.download_button(
            label="📦 Snapshot (.json)",
            data=export_analytics_snapshot_json(bundle),
            file_name="analytics_snapshot.json",
            mime="application/json",
        )
