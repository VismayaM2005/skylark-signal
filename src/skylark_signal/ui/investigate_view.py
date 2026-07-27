import streamlit as st
from typing import List, Any
from skylark_signal.ui.filters import render_filter_bar
from skylark_signal.ui.components import render_metric_card, render_trust_badge
from skylark_signal.ui.charts import (
    create_pipeline_funnel_chart,
    create_revenue_at_risk_chart,
    create_sector_matrix_chart
)
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.analytics.formatting import format_currency, format_percentage

def render_investigate_view(deals: List[Any], work_orders: List[Any]):
    """Renders the executive dashboard Investigate view."""
    st.markdown("### 📊 Business Intelligence Dashboard")
    st.caption("Visual operational dashboard with real-time metrics, risk models, and sector performance.")

    # 1. Filter Bar
    filt_deals, filt_wo = render_filter_bar(deals, work_orders)

    # 2. Compute Analytics for Filtered Dataset
    bundle = build_full_analytics_bundle(filt_deals, filt_wo)

    p_m = bundle["pipeline_metrics"]
    o_m = bundle["operations_metrics"]
    cb_m = bundle["cross_board_metrics"]
    r_m = bundle["revenue_at_risk"]
    att_queue = bundle["attention_queue"]
    t_m = bundle["data_trust_score"]

    st.markdown("---")
    # 3. KPI Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Total Open Pipeline", format_currency(p_m["total_open_pipeline"]), f"{p_m['open_deals']} Open Deals")
    with col2:
        render_metric_card("Weighted Pipeline", format_currency(p_m["weighted_pipeline"]), f"Win Rate: {format_percentage(p_m['win_rate'])}")
    with col3:
        render_metric_card("Active Work Orders", str(o_m["active_work_orders"]), f"{o_m['overdue_work_orders']} Overdue | {o_m['blocked_work_orders']} Blocked")
    with col4:
        render_metric_card("Revenue at Risk", format_currency(r_m["total_revenue_at_risk"]), f"{r_m['risk_items_count']} Risk Buckets")

    st.markdown("---")
    # 4. Founder Attention Queue Table
    st.markdown("#### 🚨 Founder Attention Queue")
    st.caption("Ranked priority items requiring operational or executive intervention:")

    if att_queue:
        queue_df = [
            {
                "Rank": item["rank"],
                "Priority": item["priority"],
                "Title": item["title"],
                "Impact (INR)": format_currency(item["financial_impact"]),
                "Score": f"{item['total_score']:.1f}",
                "Board": item["source_board"],
                "Recommended Action": item["recommended_action"]
            }
            for item in att_queue
        ]
        st.dataframe(queue_df, use_container_width=True)
    else:
        st.success("✓ Zero critical attention items logged for current filters.")

    st.markdown("---")
    # 5. Interactive Plotly Charts
    c1, c2 = st.columns(2)
    with c1:
        if p_m["pipeline_by_stage"]:
            fig_funnel = create_pipeline_funnel_chart(p_m["pipeline_by_stage"])
            st.plotly_chart(fig_funnel, use_container_width=True)
    with c2:
        if r_m["risk_breakdown_by_category"]:
            fig_risk = create_revenue_at_risk_chart(r_m["risk_breakdown_by_category"])
            st.plotly_chart(fig_risk, use_container_width=True)

    # 6. Sector Matrix Chart
    if cb_m["sector_sales_vs_execution"]:
        fig_sector = create_sector_matrix_chart(cb_m["sector_sales_vs_execution"])
        st.plotly_chart(fig_sector, use_container_width=True)

    st.markdown("---")
    # 7. Data Quality & Data Trust Summary
    render_trust_badge(t_m["combined_trust_score"], t_m["trust_rating"])
    
    with st.expander("🔍 Detailed Data Quality Component Breakdown"):
        d_cols = st.columns(3)
        with d_cols[0]:
            st.write("**Deals Board Completeness:**")
            st.write(f"- Deal Values: `{t_m['component_scores']['deals_value_completeness']}%`")
            st.write(f"- Closure Probabilities: `{t_m['component_scores']['deals_probability_completeness']}%`")
            st.write(f"- Close Dates: `{t_m['component_scores']['deals_date_completeness']}%`")
        with d_cols[1]:
            st.write("**Work Orders Board Completeness:**")
            st.write(f"- Primary Key Validity: `{t_m['component_scores']['work_orders_id_validity']}%`")
            st.write(f"- Contract Values: `{t_m['component_scores']['work_orders_value_completeness']}%`")
            st.write(f"- Target Dates: `{t_m['component_scores']['work_orders_date_completeness']}%`")
        with d_cols[2]:
            st.write("**Cross-Board Account Linkage:**")
            st.write(f"- Account Match Coverage: `{t_m['account_match_coverage_score']}%`")
            st.write(f"- Shared Customer Accounts: `{cb_m['shared_customer_accounts']}`")
