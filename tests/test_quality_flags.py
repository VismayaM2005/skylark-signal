import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.quality import QualityFlag, create_quality_flag
from skylark_signal.data.exporters import get_highest_severity, format_flag_summary

def test_quality_flag_creation():
    flag = create_quality_flag(
        code="missing_deal_value",
        severity="info",
        message="Deal value is missing",
        field="deal_value",
        affects_metrics=True
    )
    assert flag.code == "missing_deal_value"
    assert flag.severity == "info"
    assert flag.affects_metrics is True

def test_flag_severity_and_summary():
    flag1 = create_quality_flag("info_code", "info", "Info msg")
    flag2 = create_quality_flag("warn_code", "warning", "Warning msg")
    flag3 = create_quality_flag("err_code", "error", "Error msg")

    assert get_highest_severity([flag1, flag2]) == "warning"
    assert get_highest_severity([flag1, flag2, flag3]) == "error"
    assert get_highest_severity([]) == "clean"

    summary = format_flag_summary([flag1, flag2])
    assert "[info_code] Info msg" in summary
    assert "[warn_code] Warning msg" in summary
