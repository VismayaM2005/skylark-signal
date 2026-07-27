import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.reporting.export import (
    export_leadership_brief_markdown,
    export_attention_queue_csv,
    export_evidence_bundle_csv,
    export_analytics_snapshot_json
)

def test_reporting_export_functions():
    bundle = {
        "leadership_brief": {
            "overall_status": "AMBER",
            "generation_timestamp": "2026-07-27T10:00:00Z",
            "executive_pulse": "Pulse statement.",
            "five_numbers_to_quote": [{"label": "Open Pipeline", "value": "100 INR"}],
            "top_wins": ["Win 1"],
            "top_risks": ["Risk 1"],
            "pipeline_summary": "Pipeline summary.",
            "execution_summary": "Execution summary.",
            "revenue_at_risk_summary": "Risk summary.",
            "decisions_required": ["Dec 1"],
            "recommended_actions": ["Act 1"],
            "data_trust_summary": "Trust 80."
        },
        "attention_queue": [
            {"rank": 1, "priority": "P1", "title": "Issue 1", "total_score": 90.0}
        ],
        "evidence_counts": {"open_pipeline": 5}
    }

    md_str = export_leadership_brief_markdown(bundle)
    assert "Founder Leadership Brief" in md_str

    att_csv = export_attention_queue_csv(bundle)
    assert "Issue 1" in att_csv

    evi_csv = export_evidence_bundle_csv(bundle)
    assert "open_pipeline,5" in evi_csv

    json_str = export_analytics_snapshot_json(bundle)
    assert "leadership_brief" in json_str
