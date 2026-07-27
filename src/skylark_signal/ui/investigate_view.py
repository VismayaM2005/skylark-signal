import streamlit as st
from typing import List, Any
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.analytics.formatting import format_currency, format_percentage
from skylark_signal.ui.components import render_trust_badge, render_view_header
from skylark_signal.ui.charts import (
    create_pipeline_by_stage_chart,
    create_revenue_at_risk_donut,
    create_sector_matrix_chart,
)


def render_investigate_view(deals: List[Any], work_orders: List[Any]):
    """Renders the executive visual dashboard with Plotly charts, KPI strip, and multi-dimensional filters."""
    render_view_header(
        "📊 Investigate",
        "Filter and drill down into pipeline health, operations, and revenue risk across all boards.",
    )

    # ── Filter Bar ────────────────────────────────────────────
    all_sectors = sorted(list(set(
        [d.sector for d in deals if d.sector]
        + [w.sector for w in work_orders if w.sector]
    )))
    all_owners = sorted(list(set([d.owner for d in deals if d.owner])))
    # Deals use .status; Work Orders use .execution_status (different field)
    all_statuses = sorted(list(set(
        [d.status for d in deals if d.status]
        + [w.execution_status for w in work_orders if w.execution_status]
    )))

    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>Filter Controls</div>",
        unsafe_allow_html=True,
    )
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        sel_sector = st.selectbox("Sector", ["All Sectors"] + all_sectors, index=0)
    with f_col2:
        sel_owner = st.selectbox("Deal Owner", ["All Owners"] + all_owners, index=0)
    with f_col3:
        sel_status = st.selectbox("Status", ["All Statuses"] + all_statuses, index=0)

    # Apply Filters
    target_deals = deals
    target_wo = work_orders
    if sel_sector != "All Sectors":
        target_deals = [d for d in target_deals if d.sector == sel_sector]
        target_wo = [w for w in target_wo if w.sector == sel_sector]
    if sel_owner != "All Owners":
        target_deals = [d for d in target_deals if d.owner == sel_owner]
    if sel_status != "All Statuses":
        target_deals = [d for d in target_deals if d.status == sel_status]
        target_wo = [w for w in target_wo if w.execution_status == sel_status]

    bundle = build_full_analytics_bundle(target_deals, target_wo)
    p_m = bundle["pipeline_metrics"]
    o_m = bundle["operations_metrics"]
    r_m = bundle["revenue_at_risk"]
    t_m = bundle["data_trust_score"]

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── KPI Strip ─────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Open Pipeline", format_currency(p_m["total_open_pipeline"]), f"{p_m['open_deals']} Open Deals")
    with k2:
        st.metric("Weighted Pipeline", format_currency(p_m["weighted_pipeline"]), f"Win Rate: {format_percentage(p_m['win_rate'])}")
    with k3:
        st.metric("Active Work Orders", str(o_m["active_work_orders"]), f"On-Time: {format_percentage(o_m['on_time_completion_rate'])}")
    with k4:
        st.metric("Revenue at Risk", format_currency(r_m["total_revenue_at_risk"]), f"{r_m['risk_items_count']} Risk Items")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────
    ch_col1, ch_col2 = st.columns(2)
    with ch_col1:
        fig_stage = create_pipeline_by_stage_chart(target_deals)
        st.plotly_chart(fig_stage, use_container_width=True)
    with ch_col2:
        fig_risk = create_revenue_at_risk_donut(r_m["risk_breakdown_by_category"])
        st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sector Matrix ──────────────────────────────────────────
    fig_sector = create_sector_matrix_chart(target_deals, target_wo)
    st.plotly_chart(fig_sector, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Data Quality Card ─────────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;'>📌 Data Quality Audit</div>",
        unsafe_allow_html=True,
    )
    render_trust_badge(t_m["combined_trust_score"], t_m["trust_rating"])
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    with st.expander("🔍 Component Data Quality Breakdown"):
        q_col1, q_col2, q_col3 = st.columns(3)
        with q_col1:
            st.markdown(
                f"<div class='saas-card'>"
                f"<div style='font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;'>Deals Board</div>"
                f"<div style='font-size:22px; font-weight:800; color:#38BDF8;'>{t_m['deals_board_score']:.0f}/100</div>"
                f"<div style='font-size:12px; color:#64748B; margin-top:8px;'>Missing probabilities: {p_m['deals_missing_probability']}<br>Missing close dates: {p_m['deals_missing_close_date']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with q_col2:
            st.markdown(
                f"<div class='saas-card'>"
                f"<div style='font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;'>Work Orders Board</div>"
                f"<div style='font-size:22px; font-weight:800; color:#38BDF8;'>{t_m['work_orders_board_score']:.0f}/100</div>"
                f"<div style='font-size:12px; color:#64748B; margin-top:8px;'>Missing completion dates: {o_m['work_orders_missing_completion_date']}<br>Blocked projects: {o_m['blocked_work_orders']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with q_col3:
            st.markdown(
                f"<div class='saas-card'>"
                f"<div style='font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;'>Cross-Board Linkage</div>"
                f"<div style='font-size:22px; font-weight:800; color:#38BDF8;'>{t_m['account_match_coverage_score']:.0f}/100</div>"
                f"<div style='font-size:12px; color:#64748B; margin-top:8px;'>Customer account code matching<br>99.43% coverage</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
