import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.normalizer import RecordNormalizer

def test_normalize_deal_record():
    normalizer = RecordNormalizer()
    raw_row = {
        "source_file": "deals.xlsx",
        "source_sheet": "Deal tracker",
        "source_row_number": 5,
        "file_hash": "DUMMYHASH123",
        "raw_values": {
            "Deal Name": "Sakura",
            "Owner code": "OWNER_003",
            "Client Code": "COMPANY046",
            "Deal Status": "Won",
            "Close Date (A)": "2025-06-30 00:00:00",
            "Closure Probability": "100%",
            "Masked Deal value": "500000.0",
            "Tentative Close Date": "Q3 FY26",
            "Deal Stage": "G. Project Won",
            "Product deal": "Pure Service",
            "Sector/service": "Mining",
            "Created Date": "2025-04-01"
        }
    }

    record = normalizer.normalize_deal(raw_row)
    assert record.deal_name == "Sakura"
    assert record.customer == "COMPANY_046"
    assert record.deal_id.startswith("IMPORT-DEAL-")
    assert record.stage == "Project Won"
    assert record.status == "Won"
    assert record.sector == "Mining"
    assert record.deal_value == 500000.0
    assert record.probability == 1.0
    assert record.expected_close_date is None
    assert record.expected_close_period == "Q3 FY26"
    assert record.actual_close_date == "2025-06-30"

    # Check flags
    codes = [f.code for f in record.quality_flags]
    assert "period_without_exact_date" in codes
    assert "synthetic_deal_id" in codes
