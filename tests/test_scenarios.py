import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
import copy
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.analytics.scenarios import simulate_scenario

def test_scenario_engine_deal_slip_and_zero_mutation():
    baseline_deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="d.xlsx", source_sheet="D", source_row_number=1,
            source_record_id="D1", deal_id="DEAL-001", deal_name="Alpha", customer="C1",
            stage="E. Proposal Sent", status="Open", deal_value=1000000.0, probability=0.8,
            expected_close_date="2026-08-15"
        )
    ]
    baseline_wo = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="WO Alpha",
            customer="C1", project_value_excl_tax=500000.0, execution_status="Ongoing"
        )
    ]

    original_date = baseline_deals[0].expected_close_date

    res = simulate_scenario(
        baseline_deals=baseline_deals,
        baseline_work_orders=baseline_wo,
        scenario_type="deal_slip",
        target_record_id="DEAL-001",
        numeric_param=45.0
    )

    # 1. Verify baseline dataset was NOT mutated!
    assert baseline_deals[0].expected_close_date == original_date

    # 2. Verify scenario results
    assert res["scenario_type"] == "deal_slip"
    assert "DEAL-001" in res["affected_records"]
    assert "deltas" in res

def test_scenario_engine_deal_closed_lost():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="d.xlsx", source_sheet="D", source_row_number=1,
            source_record_id="D1", deal_id="DEAL-001", deal_name="Alpha", customer="C1",
            stage="E. Proposal Sent", status="Open", deal_value=1000000.0, probability=0.8
        )
    ]
    wo = []

    res = simulate_scenario(deals, wo, scenario_type="deal_closed_lost", target_record_id="DEAL-001")

    assert res["deltas"]["open_pipeline_delta"] == -1000000.0
    assert res["deltas"]["weighted_pipeline_delta"] == -800000.0

def test_scenario_engine_work_order_fixed():
    deals = []
    wo = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="WO Alpha",
            customer="C1", project_value_excl_tax=500000.0, execution_status="Blocked"
        )
    ]

    res = simulate_scenario(deals, wo, scenario_type="work_order_fixed", target_record_id="SDPLDEAL-001")

    assert res["deltas"]["revenue_at_risk_delta"] == -500000.0
    assert "SDPLDEAL-001" in res["affected_records"]
