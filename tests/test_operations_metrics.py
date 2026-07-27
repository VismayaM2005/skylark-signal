import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.models import CanonicalWorkOrderRecord
from skylark_signal.analytics.operations_metrics import build_operations_metrics

def test_operations_metrics_calculation():
    work_orders = [
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=1,
            source_record_id="WO1", work_order_id="SDPLDEAL-001", work_order_name="WO Alpha",
            customer="COMPANY_001", sector="Mining", project_value_excl_tax=200000.0, project_value_incl_tax=236000.0,
            execution_status="Ongoing", due_date="2025-01-01"
        ),
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=2,
            source_record_id="WO2", work_order_id="SDPLDEAL-002", work_order_name="WO Beta",
            customer="COMPANY_002", sector="Renewables", project_value_excl_tax=400000.0, project_value_incl_tax=472000.0,
            execution_status="Completed", due_date="2026-05-01", completion_date="2026-04-20"
        ),
        CanonicalWorkOrderRecord(
            source_system="Test", source_file="wo.xlsx", source_sheet="WO", source_row_number=3,
            source_record_id="WO3", work_order_id="SDPLDEAL-003", work_order_name="WO Gamma",
            customer="COMPANY_003", sector="Powerline", project_value_excl_tax=100000.0, project_value_incl_tax=118000.0,
            execution_status="Blocked"
        )
    ]

    metrics = build_operations_metrics(work_orders)

    assert metrics["total_work_orders"] == 3
    assert metrics["active_work_orders"] == 2
    assert metrics["completed_work_orders"] == 1
    assert metrics["blocked_work_orders"] == 1
    assert metrics["overdue_work_orders"] == 1
    assert metrics["average_project_value"] == 233333.33
    assert metrics["on_time_completion_rate"] == 1.0
