import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.analytics.evidence import EvidenceCollector

def test_evidence_collector():
    collector = EvidenceCollector()
    
    collector.add_evidence(
        metric_name="total_open_pipeline",
        board_name="Deals",
        source_item_id="101",
        source_record_id="SRC-REC-101",
        field_name="deal_value",
        raw_value="500000",
        normalized_value=500000.0,
        included_in_calculation=True,
        inclusion_reason="Open deal with valid deal_value"
    )

    records = collector.get_all_evidence()
    assert len(records) == 1
    assert records[0].metric_name == "total_open_pipeline"
    assert records[0].normalized_value == 500000.0

    counts = collector.count_by_metric()
    assert counts["total_open_pipeline"] == 1
