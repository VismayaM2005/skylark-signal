import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.dashboard_repository import DashboardRepository

def test_dashboard_repository_fallback_loading():
    repo = DashboardRepository(
        deals_json_path="data/processed/deals_clean.json",
        wo_json_path="data/processed/work_orders_clean.json"
    )

    deals, work_orders, status_info = repo.load_data()

    assert len(deals) == 332
    assert len(work_orders) == 176
    assert status_info["mode"] in ("PROCESSED_JSON_FALLBACK", "LIVE_MONDAY_API")
    assert "timestamp" in status_info
