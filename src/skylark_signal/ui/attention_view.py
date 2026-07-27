import streamlit as st
from typing import List, Any
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.analytics.formatting import format_currency, format_percentage
from skylark_signal.ui.components import render_trust_badge

def render_attention_view(deals: List[Any], work_orders: List[Any]):
    """Renders the dedicated Founder Attention Queue view."""
    st.markdown("### 🚨 Founder Attention Queue")
    st.caption("Ranked decision queue prioritizing operational bottlenecks, revenue risks, and key account dependencies.")

    bundle = build_full_analytics_bundle(deals, work_orders)
    queue = bundle["attention_queue"]
    trust = bundle["data_trust_score"]

    # 1. Summary KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        p1_count = len([i for i in queue if "P1" in i.get("priority", "")])
        st.metric("Critical P1 Items", str(p1_count), f"{len(queue)} Total Queue Items")
    with c2:
        top_impact = queue[0]["financial_impact"] if queue else 0.0
        st.metric("Top Item Financial Exposure", format_currency(top_impact))
    with c3:
        top_score = queue[0]["total_score"] if queue else 0.0
        st.metric("Top Item Attention Score", f"{top_score:.1f} / 100")
    with c4:
        st.metric("Data Trust Rating", f"{trust['combined_trust_score']:.1f}/100", trust['trust_rating'])

    st.markdown("---")
    # 2. Queue Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sel_prio = st.selectbox("Priority Filter", ["All Priorities", "P1-Critical", "P2-High", "P3-Medium", "P4-Low"], index=0)
    with col_f2:
        sel_board = st.selectbox("Board Filter", ["All Boards", "Work Orders Board", "Deals Board", "Cross-Board"], index=0)
    with col_f3:
        search_query = st.text_input("Search Queue Items:", placeholder="e.g. Schedule Delay, Concentration...")

    filtered_queue = queue
    if sel_prio != "All Priorities":
        prio_prefix = sel_prio.split("-")[0]
        filtered_queue = [i for i in filtered_queue if prio_prefix in i.get("priority", "")]

    if sel_board != "All Boards":
        filtered_queue = [i for i in filtered_queue if sel_board.lower() in i.get("source_board", "").lower()]

    if search_query:
        sq = search_query.lower()
        filtered_queue = [i for i in filtered_queue if sq in i.get("title", "").lower() or sq in i.get("description", "").lower()]

    st.markdown("---")
    # 3. Ranked Items Table
    st.markdown("#### 📋 Ranked Decision Items")

    if filtered_queue:
        table_data = [
            {
                "Rank": item["rank"],
                "Priority": item["priority"],
                "Title": item["title"],
                "Financial Impact (INR)": format_currency(item["financial_impact"]),
                "Score": f"{item['total_score']:.1f}",
                "Board": item["source_board"],
                "Recommended Action": item["recommended_action"]
            }
            for item in filtered_queue
        ]
        st.dataframe(table_data, use_container_width=True)

        st.markdown("---")
        # 4. Item Drill-Down Accordions
        st.markdown("#### 🔍 Item Drill-Down & Evidence Details")
        for item in filtered_queue:
            with st.expander(f"Rank #{item['rank']} | [{item['priority']}] {item['title']} — Score: {item['total_score']:.1f}"):
                st.markdown(f"**Description**: {item['description']}")
                st.markdown(f"**Why It Matters**: {item['why_it_matters']}")
                
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    st.write("**Scoring Dimensions:**")
                    st.write(f"- Financial Score: `{item['financial_impact_score']:.1f}/100`")
                    st.write(f"- Urgency Score: `{item['urgency_score']:.1f}/100`")
                    st.write(f"- Severity Score: `{item['severity_score']:.1f}/100`")
                    st.write(f"- Confidence Score: `{item['confidence_score']:.1f}/100`")
                with c_d2:
                    st.write("**Traceability & Source Metadata:**")
                    st.write(f"- Source Board: `{item['source_board']}`")
                    st.write(f"- Source Record IDs: `{', '.join(item.get('source_record_ids', []))}`")
                    st.write(f"- Rule Used: `{item['rule_used']}`")

                st.markdown("**Evidence Summary:**")
                st.info(item.get("evidence_summary", "No additional evidence summary provided."))

                st.markdown("**Recommended Next Action:**")
                st.success(f"👉 {item['recommended_action']}")
    else:
        st.info("No items match current filter criteria.")

    st.markdown("---")
    # 5. How Ranking Works Note
    with st.expander("ℹ️ How Attention Queue Ranking Works"):
        st.markdown("""
        The **Founder Attention Queue** uses a multi-dimensional deterministic scoring formula to rank issues:
        $$\\text{Total Score} = (0.40 \\times \\text{Financial Impact}) + (0.30 \\times \\text{Urgency}) + (0.20 \\times \\text{Severity}) + (0.10 \\times \\text{Confidence})$$
        
        - **Financial Impact (40%)**: Logarithmic scaling of exposure from 10 to 100.
        - **Urgency (30%)**: Time-sensitivity (past due dates, immediate SLA breach).
        - **Severity (20%)**: Operational impact (blocked delivery vs missing data).
        - **Confidence (10%)**: Data quality and source record completeness.
        """)
