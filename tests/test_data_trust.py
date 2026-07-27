import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.reporting.data_trust import build_data_trust_score

def test_data_trust_score_calculation():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=1,
            source_record_id="REC1", deal_id="DEAL-001", deal_name="Alpha", customer="COMPANY_001",
            stage="A. Lead Generated", status="Open", deal_value=1000000.0, probability=0.8,
            expected_close_date="2026-08-15"
        )
    ]

    work_orders = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="WO Alpha",
            customer="COMPANY_001", project_value_excl_tax=500000.0, due_date="2026-06-30",
            execution_status="Ongoing"
        )
    ]

    trust_score = build_data_trust_score(deals, work_orders)

    assert 0.0 <= trust_score["combined_trust_score"] <= 100.0
    assert "trust_rating" in trust_score
    assert trust_score["account_match_coverage_score"] == 100.0
    assert "component_scores" in trust_score
