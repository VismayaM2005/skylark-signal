import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.models import CanonicalDealRecord
from skylark_signal.analytics.pipeline_metrics import build_pipeline_metrics

def test_pipeline_metrics_calculation():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=1,
            source_record_id="REC1", deal_id="DEAL-001", deal_name="Alpha", customer="COMPANY_001",
            sector="Mining", stage="A. Lead Generated", status="Open", deal_value=1000000.0, probability=0.8,
            expected_close_date="2026-08-15"
        ),
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=2,
            source_record_id="REC2", deal_id="DEAL-002", deal_name="Beta", customer="COMPANY_002",
            sector="Renewables", stage="G. Project Won", status="Won", deal_value=500000.0, probability=1.0,
            actual_close_date="2026-05-10"
        ),
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=3,
            source_record_id="REC3", deal_id="DEAL-003", deal_name="Gamma", customer="COMPANY_001",
            sector="Mining", stage="L. Project Lost", status="Dead", deal_value=300000.0, probability=0.0
        )
    ]

    metrics = build_pipeline_metrics(deals)

    assert metrics["total_deals"] == 3
    assert metrics["open_deals"] == 1
    assert metrics["won_deals"] == 1
    assert metrics["lost_deals"] == 1
    assert metrics["total_open_pipeline"] == 1000000.0
    assert metrics["weighted_pipeline"] == 800000.0
    assert metrics["win_rate"] == 0.5
    assert metrics["customer_concentration_top_3"] == 100.0
