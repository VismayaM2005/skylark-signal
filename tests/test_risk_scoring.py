import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.analytics.risk import build_revenue_at_risk

def test_revenue_at_risk_non_overlapping_bucketing():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=1,
            source_record_id="D1", deal_id="DEAL-001", deal_name="Stale Proposal", customer="COMPANY_001",
            stage="E. Proposal Sent", status="Open", deal_value=1000000.0, expected_close_date="2025-01-01"
        )
    ]

    work_orders = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="Blocked Site",
            customer="COMPANY_001", project_value_excl_tax=500000.0, execution_status="Blocked"
        )
    ]

    risk_bundle = build_revenue_at_risk(deals, work_orders)

    assert risk_bundle["double_counting_prevented"] is True
    assert risk_bundle["total_revenue_at_risk"] == 1500000.0
    assert len(risk_bundle["risk_items"]) == 2
    
    categories = [r["category"] for r in risk_bundle["risk_items"]]
    assert "blocked_or_delayed_active_work_orders" in categories
    assert "stale_late_stage_deals" in categories
