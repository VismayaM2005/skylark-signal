import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.analytics import build_full_analytics_bundle

def test_attention_queue_view_data_structure():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="d.xlsx", source_sheet="D", source_row_number=1,
            source_record_id="D1", deal_id="DEAL-001", deal_name="Stale Deal", customer="C1",
            stage="E. Proposal Sent", status="Open", deal_value=1000000.0, expected_close_date="2025-01-01"
        )
    ]
    work_orders = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="Blocked WO",
            customer="C1", project_value_excl_tax=500000.0, execution_status="Blocked"
        )
    ]

    bundle = build_full_analytics_bundle(deals, work_orders)
    queue = bundle["attention_queue"]

    assert len(queue) >= 2
    assert queue[0]["rank"] == 1
    assert "priority" in queue[0]
    assert "financial_impact" in queue[0]
    assert "why_it_matters" in queue[0]
    assert "recommended_action" in queue[0]
    assert "rule_used" in queue[0]

    # Verify descending score sort
    scores = [item["total_score"] for item in queue]
    assert scores == sorted(scores, reverse=True)
