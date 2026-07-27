import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.dashboard_repository import DashboardRepository

def test_dashboard_repository_data_source_mode():
    repo = DashboardRepository()
    deals, wo, status_info = repo.load_data()
    
    assert "mode" in status_info
    assert "is_live" in status_info
    assert len(deals) > 0
    assert len(wo) > 0

def test_decision_log_deliverable_exists():
    log_path = os.path.abspath("docs/DECISION_LOG.md")
    assert os.path.exists(log_path)
    
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# Skylark Signal - Architecture & Executive Decision Log" in content
    assert "Key Technical & Data Assumptions" in content
    assert "Trade-Offs Chosen & Rationale" in content or "Trade-Offs" in content
    assert "Leadership Updates" in content
