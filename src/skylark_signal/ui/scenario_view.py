import streamlit as st
import pandas as pd
from typing import List, Any
from skylark_signal.analytics.scenarios import simulate_scenario
from skylark_signal.analytics.pipeline_metrics import is_open_deal
from skylark_signal.analytics.formatting import format_currency, format_percentage
from skylark_signal.ui.components import render_view_header


# Scenario names must match what simulate_scenario() expects
SCENARIO_DESCRIPTIONS = {
    "deal_slip":                      "Simulate a top deal's closing date slipping by N days.",
    "deal_closed_lost":               "Simulate an active deal being marked Closed Lost.",
    "deal_closed_won":                "Simulate an active deal being marked Closed Won.",
    "work_order_fixed":               "Simulate an overdue/blocked work order being resolved.",
    "deal_probability_drop":          "Simulate win probability dropping for late-stage deals.",
    "sector_pipeline_shift":          "Simulate a % shift in pipeline value for a sector.",
    "exclude_customer_concentration": "Simulate excluding a key customer to measure concentration risk.",
    "new_overdue_work_order":         "Simulate a new overdue work order entering operations.",
}

SCENARIO_ICONS = {
    "deal_slip":                      "📅",
    "deal_closed_lost":               "❌",
    "deal_closed_won":                "✅",
    "work_order_fixed":               "🔧",
    "deal_probability_drop":          "📉",
    "sector_pipeline_shift":          "🔀",
    "exclude_customer_concentration": "🚫",
    "new_overdue_work_order":         "⚠️",
}


def _delta_color(value: float) -> str:
    if value > 0:
        return "#34D399"
    elif value < 0:
        return "#F87171"
    return "#94A3B8"


def render_scenario_view(deals: List[Any], work_orders: List[Any]):
    """Renders the Scenario Simulator with side-by-side baseline/scenario comparison and delta table."""
    render_view_header(
        "🔮 Scenario Simulator",
        "Model hypothetical business changes deterministically — no board records are ever modified.",
    )

    # ── Control Panel ─────────────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;'>⚙ Scenario Control Panel</div>",
        unsafe_allow_html=True,
    )

    col_type, col_param1, col_param2 = st.columns([1, 1, 1])

    with col_type:
        scenario_type = st.selectbox(
            "Scenario Type:",
            list(SCENARIO_DESCRIPTIONS.keys()),
            format_func=lambda x: f"{SCENARIO_ICONS.get(x, '▸')} {x.replace('_', ' ').title()}",
            index=0,
        )
        st.markdown(
            f"<div style='font-size:12px; color:#475569; margin-top:6px; padding:8px 10px; background:rgba(56,189,248,0.04); border-radius:8px; border:1px solid rgba(56,189,248,0.08);'>💡 {SCENARIO_DESCRIPTIONS[scenario_type]}</div>",
            unsafe_allow_html=True,
        )

    # target_record_id is the unified param for simulate_scenario()
    target_record_id = None
    target_customer = None
    target_sector = None
    numeric_param = 30.0

    # Open deals: use is_open_deal() from analytics
    open_deals = [d for d in deals if is_open_deal(d)]
    # Active work orders: execution_status != "Completed"
    active_wo = [w for w in work_orders if (w.execution_status or "").lower() not in ("completed", "done")]

    with col_param1:
        if scenario_type in ["deal_slip", "deal_closed_lost", "deal_closed_won", "deal_probability_drop"]:
            d_options = [f"{d.deal_name} ({d.deal_id}) — {format_currency(d.deal_value)}" for d in open_deals]
            if d_options:
                sel_d = st.selectbox("Target Deal", d_options, index=0)
                target_record_id = open_deals[d_options.index(sel_d)].deal_id
            else:
                st.caption("No open deals found.")

        elif scenario_type == "work_order_fixed":
            w_options = [f"WO #{w.work_order_id} — {w.customer} ({w.execution_status})" for w in active_wo]
            if w_options:
                sel_w = st.selectbox("Target Work Order", w_options, index=0)
                target_record_id = active_wo[w_options.index(sel_w)].work_order_id
            else:
                st.caption("No active work orders found.")

        elif scenario_type == "exclude_customer_concentration":
            cust_options = sorted(list(set([d.customer for d in deals if d.customer])))
            if cust_options:
                target_customer = st.selectbox("Target Customer", cust_options, index=0)

        elif scenario_type == "sector_pipeline_shift":
            sector_options = sorted(list(set([d.sector for d in deals if d.sector])))
            if sector_options:
                target_sector = st.selectbox("Target Sector", sector_options, index=0)

        elif scenario_type == "new_overdue_work_order":
            st.caption("Simulates an existing active work order overrunning its due date.")

    with col_param2:
        if scenario_type == "deal_slip":
            numeric_param = float(st.number_input("Slip Days", min_value=1, max_value=180, value=30))
        elif scenario_type == "deal_probability_drop":
            numeric_param = float(st.slider("Probability Drop (%)", min_value=5, max_value=90, value=20))
        elif scenario_type == "sector_pipeline_shift":
            numeric_param = float(st.slider("Pipeline Shift (%)", min_value=-50, max_value=100, value=20))
        elif scenario_type == "new_overdue_work_order":
            numeric_param = float(st.number_input("Simulated WO Value (₹)", min_value=100_000, value=2_500_000, step=500_000))

    # ── Run Simulation ────────────────────────────────────────
    res = simulate_scenario(
        baseline_deals=deals,
        baseline_work_orders=work_orders,
        scenario_type=scenario_type,
        target_record_id=target_record_id,
        numeric_param=numeric_param,
        target_sector=target_sector,
        target_customer=target_customer,
    )

    # The bundle keys are baseline_bundle and scenario_bundle
    base_bundle = res["baseline_bundle"]
    scen_bundle = res["scenario_bundle"]
    deltas = res["deltas"]

    base_p = base_bundle["pipeline_metrics"]
    scen_p = scen_bundle["pipeline_metrics"]
    base_r = base_bundle["revenue_at_risk"]
    scen_r = scen_bundle["revenue_at_risk"]

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:14px;'>📊 Baseline vs. Scenario Comparison</div>",
        unsafe_allow_html=True,
    )

    # ── Comparison Cards ──────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    comparisons = [
        (c1, "Open Pipeline",    "💼", base_p["total_open_pipeline"],  scen_p["total_open_pipeline"],  deltas["open_pipeline_delta"],    False),
        (c2, "Weighted Pipeline","📈", base_p["weighted_pipeline"],    scen_p["weighted_pipeline"],    deltas["weighted_pipeline_delta"], False),
        (c3, "Revenue at Risk",  "⚠️", base_r["total_revenue_at_risk"],scen_r["total_revenue_at_risk"],deltas["revenue_at_risk_delta"],   True),
    ]

    for col, label, icon, base_val, scen_val, delta_val, invert in comparisons:
        # For revenue at risk: positive delta = worse, so invert color
        d_color = _delta_color(-delta_val if invert else delta_val)
        sign = "+" if delta_val > 0 else ""
        with col:
            st.markdown(
                f"""
                <div class="saas-card">
                    <div style="font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;">
                        {icon} {label}
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
                        <div>
                            <div style="font-size:10px; color:#334155; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Baseline</div>
                            <div style="font-size:16px; font-weight:700; color:#94A3B8;">{format_currency(base_val)}</div>
                        </div>
                        <div>
                            <div style="font-size:10px; color:#334155; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Scenario</div>
                            <div style="font-size:16px; font-weight:700; color:#F0F8FF;">{format_currency(scen_val)}</div>
                        </div>
                    </div>
                    <div style="padding:8px 12px; background:rgba(0,0,0,0.2); border-radius:8px; font-size:13px;">
                        <span style="color:#475569;">Δ Delta:</span>
                        <span style="color:{d_color}; font-weight:700; margin-left:6px;">{sign}{format_currency(delta_val)}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Explanation banner
    if res.get("explanation"):
        st.markdown(
            f"<div style='padding:10px 14px; background:rgba(56,189,248,0.06); border:1px solid rgba(56,189,248,0.1); border-radius:10px; font-size:13px; color:#94A3B8; margin-top:4px;'>"
            f"💡 <b>Scenario:</b> {res['explanation']}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Delta Table ───────────────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;'>📋 Full Metric Delta Summary</div>",
        unsafe_allow_html=True,
    )

    base_stale = base_p.get("stale_deals", 0)
    scen_stale = scen_p.get("stale_deals", 0)
    base_status = base_bundle["leadership_brief"].get("overall_status", "—")
    scen_status = scen_bundle["leadership_brief"].get("overall_status", "—")

    df_delta = pd.DataFrame([
        {"Metric": "Open Pipeline",     "Baseline": format_currency(base_p["total_open_pipeline"]),   "Scenario": format_currency(scen_p["total_open_pipeline"]),   "Delta": f"{'+' if deltas['open_pipeline_delta'] >= 0 else ''}{format_currency(deltas['open_pipeline_delta'])}"},
        {"Metric": "Weighted Pipeline", "Baseline": format_currency(base_p["weighted_pipeline"]),     "Scenario": format_currency(scen_p["weighted_pipeline"]),     "Delta": f"{'+' if deltas['weighted_pipeline_delta'] >= 0 else ''}{format_currency(deltas['weighted_pipeline_delta'])}"},
        {"Metric": "Revenue at Risk",   "Baseline": format_currency(base_r["total_revenue_at_risk"]), "Scenario": format_currency(scen_r["total_revenue_at_risk"]), "Delta": f"{'+' if deltas['revenue_at_risk_delta'] >= 0 else ''}{format_currency(deltas['revenue_at_risk_delta'])}"},
        {"Metric": "Stale Deals",       "Baseline": str(base_stale),                                  "Scenario": str(scen_stale),                                  "Delta": f"{scen_stale - base_stale:+d}"},
        {"Metric": "Executive Health",  "Baseline": base_status,                                      "Scenario": scen_status,                                      "Delta": "→ " + scen_status},
    ])
    st.dataframe(df_delta, use_container_width=True, hide_index=True)
