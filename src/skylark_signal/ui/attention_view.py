import streamlit as st
from typing import List, Any
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.analytics.formatting import format_currency
from skylark_signal.ui.components import render_view_header


_PRIORITY_META = {
    "P1": {"cls": "badge-p1", "left_color": "#EF4444", "bg": "rgba(127,29,29,0.04)"},
    "P2": {"cls": "badge-p2", "left_color": "#F59E0B", "bg": "rgba(120,53,15,0.04)"},
    "P3": {"cls": "badge-p3", "left_color": "#3B82F6", "bg": "rgba(30,58,138,0.04)"},
    "P4": {"cls": "badge-p4", "left_color": "#22C55E", "bg": "rgba(20,83,45,0.04)"},
}


def _get_priority_key(p_code: str) -> str:
    for k in ["P1", "P2", "P3", "P4"]:
        if k in p_code:
            return k
    return "P3"


def render_attention_view(deals: List[Any], work_orders: List[Any]):
    """Renders the Founder Attention Queue with P1-P4 priority cards and expandable evidence drill-downs."""
    render_view_header(
        "🚨 Founder Attention Queue",
        "Priority-ranked issues by financial impact, urgency, and confidence — requiring founder decisions.",
    )

    bundle = build_full_analytics_bundle(deals, work_orders)
    att_queue = bundle["attention_queue"]

    # ── Filter Controls ───────────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>Filter Queue</div>",
        unsafe_allow_html=True,
    )
    col_p, col_b, col_s = st.columns([1, 1, 2])
    with col_p:
        sel_priority = st.selectbox("Priority", ["All Priorities", "P1-Critical", "P2-High", "P3-Medium", "P4-Low"])
    with col_b:
        sel_board = st.selectbox("Source Board", ["All Boards", "Deals Board", "Work Orders Board"])
    with col_s:
        search_term = st.text_input("Search", placeholder="Filter by customer, deal, or issue…")

    # Apply Filters
    filtered_items = att_queue
    if sel_priority != "All Priorities":
        p_prefix = sel_priority.split("-")[0]
        filtered_items = [i for i in filtered_items if i.get("priority", "").startswith(p_prefix)]
    if sel_board != "All Boards":
        b_term = "Deals" if "Deals" in sel_board else "Work Orders"
        filtered_items = [i for i in filtered_items if b_term.lower() in i.get("source_board", "").lower()]
    if search_term:
        term = search_term.lower()
        filtered_items = [
            i for i in filtered_items
            if term in i.get("title", "").lower() or term in i.get("why_it_matters", "").lower()
        ]

    # ── Summary Stats ─────────────────────────────────────────
    p1_count = sum(1 for i in filtered_items if "P1" in i.get("priority", ""))
    p2_count = sum(1 for i in filtered_items if "P2" in i.get("priority", ""))
    total_impact = sum(i.get("financial_impact", 0.0) for i in filtered_items)

    st.markdown("<hr>", unsafe_allow_html=True)

    stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
    with stat_c1:
        st.metric("Total Items", len(filtered_items))
    with stat_c2:
        st.metric("P1-Critical", p1_count)
    with stat_c3:
        st.metric("P2-High", p2_count)
    with stat_c4:
        st.metric("Total Impact", format_currency(total_impact))

    st.markdown("<hr>", unsafe_allow_html=True)

    if not filtered_items:
        st.markdown(
            """
            <div style="text-align:center; padding:48px; color:#334155;">
                <div style="font-size:28px; margin-bottom:8px;">✓</div>
                <div style="font-size:15px; font-weight:600; color:#475569;">No items match the current filter.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Priority Cards ────────────────────────────────────────
    for item in filtered_items:
        p_code = item.get("priority", "P3")
        p_key = _get_priority_key(p_code)
        meta = _PRIORITY_META[p_key]

        score = item.get("total_score", 0.0)
        impact = format_currency(item.get("financial_impact", 0.0))
        urgency = item.get("urgency_label", "Medium")
        source = item.get("source_board", "Board")
        rank = item.get("rank", 1)
        title = item.get("title", "Issue Item")
        why = item.get("why_it_matters", "")

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, {meta['bg']}, #0A1628);
                border: 1px solid rgba(56,189,248,0.08);
                border-left: 3px solid {meta['left_color']};
                border-radius: 0 14px 14px 0;
                padding: 18px 22px;
                margin-bottom: 12px;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span class="{meta['cls']}"># {rank} {p_code}</span>
                        <span style="font-size:16px; font-weight:700; color:#F0F8FF;">{title}</span>
                    </div>
                    <span style="font-size:12px; font-weight:700; color:#38BDF8; background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.15); padding:3px 10px; border-radius:8px;">
                        Score: {score:.1f}/100
                    </span>
                </div>
                <div style="font-size:13px; color:#64748B; line-height:1.6; margin-bottom:12px;">{why}</div>
                <div style="display:flex; gap:24px; flex-wrap:wrap; font-size:12px;">
                    <div style="color:#94A3B8;">💰 Impact: <strong style="color:#F0F8FF;">{impact}</strong></div>
                    <div style="color:#94A3B8;">⏳ Urgency: <strong style="color:#F0F8FF;">{urgency}</strong></div>
                    <div style="color:#94A3B8;">📂 Source: <strong style="color:#F0F8FF;">{source}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"🔍 Evidence & Source Records — #{rank} {title}"):
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.markdown(
                    f"<div style='font-size:12px; color:#475569; margin-bottom:4px;'>RECOMMENDED ACTION</div>"
                    f"<div style='font-size:13px; color:#CBD5E1; padding:10px 12px; background:rgba(56,189,248,0.04); border:1px solid rgba(56,189,248,0.08); border-radius:8px;'>"
                    f"{item.get('recommended_action', '—')}</div>",
                    unsafe_allow_html=True,
                )
            with detail_col2:
                st.markdown(
                    f"<div style='font-size:12px; color:#475569; margin-bottom:4px;'>SOURCE RECORD IDs</div>"
                    f"<div style='font-size:13px; color:#38BDF8; font-family:monospace; padding:10px 12px; background:rgba(56,189,248,0.04); border:1px solid rgba(56,189,248,0.08); border-radius:8px;'>"
                    f"{', '.join(item.get('source_record_ids', []))}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<div style='margin-top:10px; font-size:12px; color:#64748B;'><b style='color:#94A3B8;'>Evidence:</b> {item.get('evidence_summary', '')}</div>",
                unsafe_allow_html=True,
            )
            st.code(f"Formula: {item.get('formula_used', '')}", language="text")
