import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.analytics.leadership import build_leadership_brief
from skylark_signal.reporting.executive_summary import format_leadership_brief_markdown

def test_leadership_brief_generation():
    deals = []
    work_orders = []
    p_metrics = {"total_open_pipeline": 5000000.0, "weighted_pipeline": 3000000.0, "open_deals": 10, "average_deal_value": 500000.0, "win_rate": 0.55}
    o_metrics = {"active_work_orders": 8, "blocked_work_orders": 1, "delayed_work_orders": 2, "completed_work_orders": 20, "average_project_value": 250000.0}
    cb_metrics = {"work_orders_linked_to_shared_customers": 25}
    risk_bundle = {"total_revenue_at_risk": 1500000.0, "risk_items_count": 2}
    att_queue = []
    trust_score = {"combined_trust_score": 82.5, "trust_rating": "MODERATE TRUST (GOOD)"}

    brief = build_leadership_brief(
        deals, work_orders, p_metrics, o_metrics, cb_metrics, risk_bundle, att_queue, trust_score
    )

    assert brief["overall_status"] in ("GREEN", "AMBER", "RED")
    assert len(brief["five_numbers_to_quote"]) == 5
    assert len(brief["top_wins"]) >= 3
    assert len(brief["top_risks"]) >= 3

    md_output = format_leadership_brief_markdown(brief)
    assert "# Skylark Signal - Founder Leadership Brief" in md_output
    assert "Executive Pulse" in md_output
    assert "Five Numbers to Quote" in md_output
