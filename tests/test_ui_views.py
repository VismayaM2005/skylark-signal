import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.data.dashboard_repository import DashboardRepository

def test_ui_imports():
    from skylark_signal.ui.styles import inject_custom_styles
    from skylark_signal.ui.charts import create_pipeline_by_stage_chart, create_revenue_at_risk_donut, create_sector_matrix_chart
    from skylark_signal.ui.status_view import render_status_view
    from skylark_signal.ui.app_shell import run_app_shell

    repo = DashboardRepository()
    deals, wo, _ = repo.load_data()

    fig1 = create_pipeline_by_stage_chart(deals)
    fig2 = create_revenue_at_risk_donut({"overdue_active_work_orders": 100.0})
    fig3 = create_sector_matrix_chart(deals, wo)

    assert fig1 is not None
    assert fig2 is not None
    assert fig3 is not None
