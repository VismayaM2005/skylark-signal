import streamlit as st
from typing import List, Any
from skylark_signal.analytics.scenarios import simulate_scenario, SCENARIO_TYPES
from skylark_signal.analytics.formatting import format_currency, format_percentage
from skylark_signal.ui.components import render_status_badge, render_trust_badge

def render_scenario_view(deals: List[Any], work_orders: List[Any]):
    """Renders the interactive Scenario Simulator UI view."""
    st.markdown("### 🔮 Scenario Simulator")
    st.caption("Hypothetical 'what if' business simulation engine. Test pipeline slippage, deal losses, and delivery fixes.")

    st.warning("⚠️ **Hypothetical Simulation Mode**: Scenarios recalculate metrics in memory and do NOT mutate live board data.")

    # 1. Interactive Control Panel
    st.markdown("#### ⚙️ Scenario Simulation Control Panel")

    col1, col2, col3 = st.columns(3)
    with col1:
        scen_labels = [s[1] for s in SCENARIO_TYPES]
        scen_keys = [s[0] for s in SCENARIO_TYPES]
        sel_label = st.selectbox("Select Scenario Type", scen_labels, index=0)
        sel_type = scen_keys[scen_labels.index(sel_label)]

    with col2:
        if sel_type in ("deal_slip", "deal_closed_lost", "deal_closed_won", "deal_probability_drop"):
            deal_options = ["First Matching Open Deal"] + [f"{d.deal_name} ({d.deal_id})" for d in deals]
            sel_deal_label = st.selectbox("Target Deal", deal_options, index=0)
            target_rec_id = sel_deal_label.split("(")[-1].replace(")", "").strip() if "(" in sel_deal_label else None
        elif sel_type == "work_order_fixed":
            wo_options = ["First Matching Active Work Order"] + [f"{w.work_order_name} ({w.work_order_id})" for w in work_orders]
            sel_wo_label = st.selectbox("Target Work Order", wo_options, index=0)
            target_rec_id = sel_wo_label.split("(")[-1].replace(")", "").strip() if "(" in sel_wo_label else None
        else:
            target_rec_id = None

    with col3:
        if sel_type == "deal_slip":
            num_param = float(st.number_input("Slippage (Days)", min_value=1, max_value=180, value=30))
        elif sel_type == "deal_probability_drop":
            num_param = float(st.slider("Probability Drop (%)", min_value=10, max_value=100, value=50))
        elif sel_type == "sector_pipeline_shift":
            num_param = float(st.slider("Pipeline Value Shift (%)", min_value=-50, max_value=50, value=-20))
        else:
            num_param = 0.0

    # Sector / Customer selectors if applicable
    target_sec = None
    target_cust = None
    if sel_type == "sector_pipeline_shift":
        sectors = sorted(list({d.sector for d in deals if d.sector}))
        target_sec = st.selectbox("Target Sector", sectors if sectors else ["Mining"])
    elif sel_type == "exclude_customer_concentration":
        customers = sorted(list({d.customer for d in deals if d.customer}))
        target_cust = st.selectbox("Target Customer", customers if customers else ["COMPANY_001"])

    run_sim = st.button("🔮 Run Scenario Simulation", type="primary")

    if run_sim or "active_scenario_result" in st.session_state:
        if run_sim:
            res = simulate_scenario(
                baseline_deals=deals,
                baseline_work_orders=work_orders,
                scenario_type=sel_type,
                target_record_id=target_rec_id,
                numeric_param=num_param,
                target_sector=target_sec,
                target_customer=target_cust
            )
            st.session_state["active_scenario_result"] = res
        else:
            res = st.session_state["active_scenario_result"]

        st.markdown("---")
        st.markdown(f"#### 📊 Simulation Results: {res['explanation']}")

        b_b = res["baseline_bundle"]
        s_b = res["scenario_bundle"]
        d = res["deltas"]

        b_p = b_b["pipeline_metrics"]
        s_p = s_b["pipeline_metrics"]
        b_r = b_b["revenue_at_risk"]
        s_r = s_b["revenue_at_risk"]

        # 2. Side-by-Side Comparison Cards
        st.markdown("##### 📈 Baseline vs Scenario Comparison")
        c_k1, c_k2, c_k3, c_k4 = st.columns(4)
        
        with c_k1:
            st.metric(
                "Total Open Pipeline",
                format_currency(s_p["total_open_pipeline"]),
                delta=format_currency(d["open_pipeline_delta"])
            )
            st.caption(f"Baseline: `{format_currency(b_p['total_open_pipeline'])}`")
            
        with c_k2:
            st.metric(
                "Weighted Pipeline",
                format_currency(s_p["weighted_pipeline"]),
                delta=format_currency(d["weighted_pipeline_delta"])
            )
            st.caption(f"Baseline: `{format_currency(b_p['weighted_pipeline'])}`")
            
        with c_k3:
            st.metric(
                "Revenue at Risk",
                format_currency(s_r["total_revenue_at_risk"]),
                delta=format_currency(d["revenue_at_risk_delta"]),
                delta_color="inverse"
            )
            st.caption(f"Baseline: `{format_currency(b_r['total_revenue_at_risk'])}`")

        with c_k4:
            st.markdown("**Executive Health Status:**")
            render_status_badge(s_b["leadership_brief"]["overall_status"])
            st.caption(f"Baseline Status: `{b_b['leadership_brief']['overall_status']}`")

        st.markdown("---")
        # 3. Delta Summary Table
        st.markdown("##### 📋 Metric Delta Summary Table")
        delta_table = [
            {"Metric Name": "Open Pipeline", "Baseline Value": format_currency(b_p["total_open_pipeline"]), "Scenario Adjusted": format_currency(s_p["total_open_pipeline"]), "Delta": format_currency(d["open_pipeline_delta"])},
            {"Metric Name": "Weighted Pipeline", "Baseline Value": format_currency(b_p["weighted_pipeline"]), "Scenario Adjusted": format_currency(s_p["weighted_pipeline"]), "Delta": format_currency(d["weighted_pipeline_delta"])},
            {"Metric Name": "Revenue at Risk", "Baseline Value": format_currency(b_r["total_revenue_at_risk"]), "Scenario Adjusted": format_currency(s_r["total_revenue_at_risk"]), "Delta": format_currency(d["revenue_at_risk_delta"])},
            {"Metric Name": "Top Attention Item", "Baseline Value": d["top_attention_item_baseline"], "Scenario Adjusted": d["top_attention_item_scenario"], "Delta": "Rank Replaced" if d["top_attention_item_baseline"] != d["top_attention_item_scenario"] else "Unchanged"},
            {"Metric Name": "Executive Status", "Baseline Value": d["executive_status_baseline"], "Scenario Adjusted": d["executive_status_scenario"], "Delta": "Status Shifted" if d["executive_status_baseline"] != d["executive_status_scenario"] else "Unchanged"}
        ]
        st.dataframe(delta_table, use_container_width=True)

        if res["affected_records"]:
            st.info(f"📂 **Records Affected**: `{', '.join(res['affected_records'])}`")

        # 4. Proof Status Block
        st.markdown("---")
        provider = st.session_state.get("llm_provider", "Deterministic")
        selected_model = st.session_state.get("selected_llm_model", "none")
        
        with st.expander("🔒 Simulation Proof & State Verification"):
            st.json({
                "simulation_mode": "HYPOTHETICAL_SCENARIO_ADJUSTED",
                "baseline_mutation": False,
                "provider": provider,
                "selected_model": selected_model,
                "used_llm": False, # Simulation is pure deterministic calculation
                "execution_path": "deterministic_scenario_engine",
                "affected_records_count": len(res["affected_records"])
            })
