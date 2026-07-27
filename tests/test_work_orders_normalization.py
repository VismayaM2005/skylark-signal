import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.normalizer import RecordNormalizer

def test_normalize_work_order_record():
    normalizer = RecordNormalizer()
    raw_row = {
        "source_file": "work_orders.xlsx",
        "source_sheet": "work order tracker",
        "source_row_number": 3,
        "file_hash": "DUMMYHASH456",
        "raw_values": {
            "Deal name masked": "Scooby-Doo",
            "Customer Name Code": "WOCOMPANY_002",
            "Serial #": "SDPLDEAL-075",
            "Nature of Work": "One time Project",
            "Execution Status": "Completed",
            "Probable Start Date": "2025-05-31",
            "Probable End Date": "2025-06-03",
            "BD/KAM Personnel code": "OWNER_003",
            "Sector": "Mining",
            "Amount in Rupees (Excl of GST) (Masked)": 100000.0,
            "Amount in Rupees (Incl of GST) (Masked)": 118000.0
        }
    }

    record = normalizer.normalize_work_order(raw_row)
    assert record.work_order_id == "SDPLDEAL-075"
    assert record.work_order_name == "Scooby-Doo"
    assert record.deal_reference is None # Must remain None
    assert record.customer == "COMPANY_002"
    assert record.sector == "Mining"
    assert record.project_value_excl_tax == 100000.0
    assert record.project_value_incl_tax == 118000.0
    assert record.implied_tax_rate == 0.18
    assert record.execution_status == "Completed"
    assert record.start_date == "2025-05-31"
    assert record.due_date == "2025-06-03"

    # Check flags
    codes = [f.code for f in record.quality_flags]
    assert "no_source_deal_reference" in codes
