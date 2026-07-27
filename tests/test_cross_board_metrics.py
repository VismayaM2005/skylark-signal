import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.analytics.cross_board_metrics import build_cross_board_metrics

def test_cross_board_account_linkage():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=1,
            source_record_id="REC1", deal_id="DEAL-001", deal_name="Alpha", customer="COMPANY_001",
            stage="G. Project Won", status="Won", deal_value=500000.0
        ),
        CanonicalDealRecord(
            source_system="Test", source_file="deals.xlsx", source_sheet="Deals", source_row_number=2,
            source_record_id="REC2", deal_id="DEAL-002", deal_name="Beta", customer="COMPANY_002",
            stage="A. Lead Generated", status="Open", deal_value=200000.0
        )
    ]

    work_orders = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="WO Alpha",
            customer="COMPANY_001", project_value_excl_tax=300000.0, execution_status="Ongoing"
        )
    ]

    metrics = build_cross_board_metrics(deals, work_orders)

    assert metrics["shared_customer_accounts"] == 1
    assert metrics["work_orders_linked_to_shared_customers"] == 1
    assert metrics["closed_won_deals_without_work_orders"] == 0
    assert metrics["match_level_distribution"]["shared_customer_match"] == 1
    assert metrics["match_level_distribution"]["confirmed_record_match"] == 0
    assert metrics["customer_level_deal_to_delivery_gap"]["COMPANY_001"] == 200000.0
