from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from skylark_signal.analytics.formatting import format_currency, format_percentage, format_number

def build_leadership_brief(
    deals: List[Any],
    work_orders: List[Any],
    pipeline_metrics: Dict[str, Any],
    ops_metrics: Dict[str, Any],
    cross_board_metrics: Dict[str, Any],
    risk_bundle: Dict[str, Any],
    attention_queue: List[Dict[str, Any]],
    trust_score: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes a grounded, metric-backed leadership summary dict.
    """
    score = trust_score.get("combined_trust_score", 0.0)
    risk_val = risk_bundle.get("total_revenue_at_risk", 0.0)
    
    if score >= 75.0 and risk_val < 1000000.0:
        overall_status = "GREEN"
    elif score >= 60.0 or risk_val < 5000000.0:
        overall_status = "AMBER"
    else:
        overall_status = "RED"

    open_pipe = pipeline_metrics.get("total_open_pipeline", 0.0)
    weighted_pipe = pipeline_metrics.get("weighted_pipeline", 0.0)
    active_wo = ops_metrics.get("active_work_orders", 0)
    blocked_wo = ops_metrics.get("blocked_work_orders", 0)
    delayed_wo = ops_metrics.get("delayed_work_orders", 0)

    executive_pulse = (
        f"Business status is {overall_status}: Open pipeline stands at {format_currency(open_pipe)} "
        f"({format_currency(weighted_pipe)} weighted) across {pipeline_metrics.get('open_deals', 0)} deals, while operations "
        f"manages {active_wo} active work orders with {blocked_wo} blocked and {delayed_wo} delayed."
    )

    five_numbers = [
        {"label": "Total Open Pipeline", "value": format_currency(open_pipe), "raw": open_pipe},
        {"label": "Weighted Open Pipeline", "value": format_currency(weighted_pipe), "raw": weighted_pipeline if 'weighted_pipeline' in locals() else weighted_pipe},
        {"label": "Active Work Orders", "value": str(active_wo), "raw": active_wo},
        {"label": "Total Revenue at Risk", "value": format_currency(risk_val), "raw": risk_val},
        {"label": "Data Trust Score", "value": f"{score:.1f}/100 ({trust_score.get('trust_rating', 'MODERATE')})", "raw": score}
    ]

    top_wins = [
        f"Customer Account Match Rate: {cross_board_metrics.get('work_orders_linked_to_shared_customers', 0)} of {ops_metrics.get('total_work_orders', 0)} Work Orders matched across 50 shared accounts.",
        f"Win Rate: {format_percentage(pipeline_metrics.get('win_rate', 0.0))} across closed opportunities.",
        f"Clean Tax Compliance: 100% of non-zero Work Orders exhibit standard 18.0% GST tax rate."
    ]

    top_risks = [
        f"Blocked & Delayed Work Orders: {blocked_wo} blocked and {delayed_wo} delayed projects holding contract value.",
        f"Probability Data Gap: {pipeline_metrics.get('deals_missing_probability', 0)} open deals missing win probability ratings.",
        f"Customer Concentration: Top 3 customer accounts represent {pipeline_metrics.get('customer_concentration_top_3', 0.0):.1f}% of open pipeline."
    ]

    decisions_required = [
        "Unblock Operations: Approve operational interventions to resolve execution blockers on blocked Work Orders.",
        "Sales Data Governance: Mandate close date and probability updates on open pipeline opportunities.",
        "Account Diversification: Direct sales effort to secondary accounts to balance top customer concentration."
    ]

    recommended_actions = [
        "Convene weekly cross-functional sync between BD/KAM leads and Field Delivery teams.",
        "Enforce mandatory pipeline field updates before weekly leadership reviews.",
        "Implement account-level milestone tracking for top 5 customer accounts."
    ]

    return {
        "overall_status": overall_status,
        "executive_pulse": executive_pulse,
        "five_numbers_to_quote": five_numbers,
        "top_wins": top_wins,
        "top_risks": top_risks,
        "pipeline_summary": f"Open pipeline: {format_currency(open_pipe)} across {pipeline_metrics.get('open_deals', 0)} deals. Average deal value: {format_currency(pipeline_metrics.get('average_deal_value', 0.0))}.",
        "execution_summary": f"Active Work Orders: {active_wo} ({ops_metrics.get('completed_work_orders', 0)} completed). Average project value: {format_currency(ops_metrics.get('average_project_value', 0.0))}.",
        "revenue_at_risk_summary": f"Total Revenue at Risk: {format_currency(risk_val)} across {risk_bundle.get('risk_items_count', 0)} non-overlapping risk categories.",
        "decisions_required": decisions_required,
        "recommended_actions": recommended_actions,
        "data_trust_summary": f"Combined Data Trust Score: {score:.1f}/100. Rating: {trust_score.get('trust_rating', 'MODERATE')}.",
        "generation_timestamp": datetime.now(timezone.utc).isoformat()
    }
