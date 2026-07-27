import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.analytics.attention_queue import build_attention_queue, calculate_financial_score

def test_financial_score_calculation():
    assert calculate_financial_score(0.0) == 10.0
    assert calculate_financial_score(200000.0) == 40.0
    assert calculate_financial_score(1500000.0) == 70.0
    assert calculate_financial_score(10000000.0) == 100.0

def test_attention_queue_ranking():
    deals = []
    work_orders = []
    risk_bundle = {"total_revenue_at_risk": 500000.0}
    p_metrics = {"customer_concentration_top_3": 55.0, "total_open_pipeline": 10000000.0, "stale_deals": 5}
    o_metrics = {"blocked_work_orders": 2, "overdue_work_orders": 10}
    cb_metrics = {}

    queue = build_attention_queue(deals, work_orders, risk_bundle, p_metrics, o_metrics, cb_metrics)

    assert len(queue) >= 3
    scores = [item["total_score"] for item in queue]
    assert scores == sorted(scores, reverse=True)
    assert queue[0]["rank"] == 1
    assert "priority" in queue[0]
