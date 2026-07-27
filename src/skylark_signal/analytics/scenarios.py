import copy
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.analytics import build_full_analytics_bundle

SCENARIO_TYPES = [
    ("deal_slip", "Top Deal Slips by X Days"),
    ("deal_closed_lost", "Deal Marked Closed Lost"),
    ("deal_closed_won", "Deal Marked Closed Won"),
    ("work_order_fixed", "Overdue/Blocked Work Order Fixed"),
    ("deal_probability_drop", "Deal Probability Reduced"),
    ("sector_pipeline_shift", "Sector Pipeline Percentage Shift"),
    ("exclude_customer_concentration", "Exclude Customer from Concentration Risk"),
    ("new_overdue_work_order", "Simulate New Overdue Work Order")
]

def simulate_scenario(
    baseline_deals: List[CanonicalDealRecord],
    baseline_work_orders: List[CanonicalWorkOrderRecord],
    scenario_type: str,
    target_record_id: str = None,
    numeric_param: float = 0.0,
    target_sector: str = None,
    target_customer: str = None
) -> Dict[str, Any]:
    """
    Pure Python scenario simulation engine.
    Deep-copies input baseline records (guaranteeing zero mutation), applies hypothetical changes,
    recomputes analytics bundle, and returns baseline, scenario, and delta summaries.
    """
    # 1. Compute baseline analytics bundle
    baseline_bundle = build_full_analytics_bundle(baseline_deals, baseline_work_orders)

    # 2. Deep copy baseline records to guarantee zero mutation
    sim_deals = copy.deepcopy(baseline_deals)
    sim_wo = copy.deepcopy(baseline_work_orders)

    affected_records = []
    explanation = ""

    # 3. Apply scenario modifications
    if scenario_type == "deal_slip":
        slip_days = int(numeric_param) if numeric_param else 30
        for d in sim_deals:
            if target_record_id and d.deal_id == target_record_id:
                old_date = d.expected_close_date or "2026-07-27"
                try:
                    dt = datetime.strptime(old_date[:10], "%Y-%m-%d")
                    new_dt = dt + timedelta(days=slip_days)
                    d.expected_close_date = new_dt.strftime("%Y-%m-%d")
                except Exception:
                    d.expected_close_date = "2026-10-01"
                affected_records.append(d.deal_id)
                explanation = f"Delayed expected close date for deal '{d.deal_name}' by {slip_days} days."
                break
        if not affected_records and sim_deals:
            # Fallback to first open deal if target_record_id not specified
            open_deals = [d for d in sim_deals if (d.status or "").lower() in ("open", "")]
            if open_deals:
                target = open_deals[0]
                target.expected_close_date = "2025-01-01" # Make past due
                affected_records.append(target.deal_id)
                explanation = f"Simulated close date delay on open deal '{target.deal_name}' ({target.deal_id})."

    elif scenario_type == "deal_closed_lost":
        for d in sim_deals:
            if (target_record_id and d.deal_id == target_record_id) or (not target_record_id and (d.status or "").lower() == "open"):
                d.status = "Dead"
                d.stage = "L. Project Lost"
                d.probability = 0.0
                affected_records.append(d.deal_id)
                explanation = f"Marked deal '{d.deal_name}' ({d.deal_id}) as Closed Lost (Dead)."
                break

    elif scenario_type == "deal_closed_won":
        for d in sim_deals:
            if (target_record_id and d.deal_id == target_record_id) or (not target_record_id and (d.status or "").lower() == "open"):
                d.status = "Won"
                d.stage = "G. Project Won"
                d.probability = 1.0
                affected_records.append(d.deal_id)
                explanation = f"Marked deal '{d.deal_name}' ({d.deal_id}) as Closed Won."
                break

    elif scenario_type == "work_order_fixed":
        for w in sim_wo:
            if (target_record_id and w.work_order_id == target_record_id) or (not target_record_id and w.execution_status == "Ongoing"):
                w.execution_status = "Completed"
                w.completion_date = "2026-07-27"
                affected_records.append(w.work_order_id)
                explanation = f"Simulated resolution and completion of Work Order '{w.work_order_name}' ({w.work_order_id})."
                break

    elif scenario_type == "deal_probability_drop":
        drop_pct = (numeric_param if numeric_param else 50.0) / 100.0
        for d in sim_deals:
            if (target_record_id and d.deal_id == target_record_id) or (not target_record_id and (d.status or "").lower() == "open" and d.probability):
                old_prob = d.probability or 0.5
                d.probability = max(0.0, old_prob - drop_pct)
                affected_records.append(d.deal_id)
                explanation = f"Reduced closure probability on deal '{d.deal_name}' from {old_prob*100:.0f}% to {d.probability*100:.0f}%."
                break

    elif scenario_type == "sector_pipeline_shift":
        shift_pct = numeric_param if numeric_param else -20.0
        multiplier = 1.0 + (shift_pct / 100.0)
        target_sec = target_sector or "Mining"
        count = 0
        for d in sim_deals:
            if d.sector == target_sec and (d.status or "").lower() in ("open", ""):
                if d.deal_value:
                    d.deal_value = round(d.deal_value * multiplier, 2)
                    affected_records.append(d.deal_id)
                    count += 1
        explanation = f"Adjusted open deal values in sector '{target_sec}' by {shift_pct:+.1f}% across {count} open deals."

    elif scenario_type == "exclude_customer_concentration":
        target_cust = target_customer or "COMPANY_001"
        count = 0
        for d in sim_deals:
            if d.customer == target_cust:
                d.customer = f"EXCLUDED_{target_cust}"
                affected_records.append(d.deal_id)
                count += 1
        explanation = f"Excluded top customer account '{target_cust}' ({count} deals) from concentration calculation."

    elif scenario_type == "new_overdue_work_order":
        for w in sim_wo:
            if w.execution_status == "Ongoing":
                w.due_date = "2025-01-01" # Set past target date
                affected_records.append(w.work_order_id)
                explanation = f"Simulated target completion date overrun on active Work Order '{w.work_order_name}' ({w.work_order_id})."
                break

    else:
        explanation = "Default baseline snapshot scenario (no modifications applied)."

    # 4. Compute scenario-adjusted analytics bundle
    scenario_bundle = build_full_analytics_bundle(sim_deals, sim_wo)

    # 5. Compute metric deltas
    b_p = baseline_bundle["pipeline_metrics"]
    s_p = scenario_bundle["pipeline_metrics"]
    b_o = baseline_bundle["operations_metrics"]
    s_o = scenario_bundle["operations_metrics"]
    b_r = baseline_bundle["revenue_at_risk"]
    s_r = scenario_bundle["revenue_at_risk"]

    deltas = {
        "open_pipeline_delta": s_p["total_open_pipeline"] - b_p["total_open_pipeline"],
        "weighted_pipeline_delta": s_p["weighted_pipeline"] - b_p["weighted_pipeline"],
        "revenue_at_risk_delta": s_r["total_revenue_at_risk"] - b_r["total_revenue_at_risk"],
        "overdue_work_orders_delta": s_o["overdue_work_orders"] - b_o["overdue_work_orders"],
        "blocked_work_orders_delta": s_o["blocked_work_orders"] - b_o["blocked_work_orders"],
        "top_attention_item_baseline": baseline_bundle["attention_queue"][0]["title"] if baseline_bundle["attention_queue"] else "None",
        "top_attention_item_scenario": scenario_bundle["attention_queue"][0]["title"] if scenario_bundle["attention_queue"] else "None",
        "executive_status_baseline": baseline_bundle["leadership_brief"]["overall_status"],
        "executive_status_scenario": scenario_bundle["leadership_brief"]["overall_status"]
    }

    return {
        "scenario_type": scenario_type,
        "explanation": explanation,
        "affected_records": affected_records,
        "baseline_bundle": baseline_bundle,
        "scenario_bundle": scenario_bundle,
        "deltas": deltas
    }
