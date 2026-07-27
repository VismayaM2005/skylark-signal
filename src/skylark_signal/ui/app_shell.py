import streamlit as st
from skylark_signal.ui.state import init_session_state
from skylark_signal.ui.components import (
    render_data_source_badge,
    render_llm_settings_sidebar,
    render_system_compliance_panel
)
from skylark_signal.ui.ask_view import render_ask_view
from skylark_signal.ui.investigate_view import render_investigate_view
from skylark_signal.ui.attention_view import render_attention_view
from skylark_signal.ui.scenario_view import render_scenario_view
from skylark_signal.ui.brief_view import render_brief_view
from skylark_signal.data.dashboard_repository import DashboardRepository

def run_app_shell():
    """Renders the main Streamlit application shell layout, 5 navigation views, and spec compliance panel."""
    st.set_page_config(
        page_title="Skylark Signal - Founder Cockpit",
        page_icon="🦅",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Header Title & Value Proposition
    st.title("🦅 Skylark Signal")
    st.caption("Founder Decision Cockpit & Risk Intelligence Agent for monday.com Deals and Work Orders boards")

    # Sidebar Navigation & Data Source Status
    st.sidebar.image("https://img.icons8.com/color/96/drone.png", width=64)
    st.sidebar.title("Navigation")
    
    render_data_source_badge(st.session_state["status_info"])

    st.sidebar.markdown("---")
    
    # Manual Data Refresh Button
    if st.sidebar.button("🔄 Refresh Board Data"):
        repo = DashboardRepository()
        deals, work_orders, status_info = repo.load_data()
        st.session_state["deals"] = deals
        st.session_state["work_orders"] = work_orders
        st.session_state["status_info"] = status_info
        st.sidebar.success("✓ Board data refreshed!")
        st.rerun()

    # Navigation Tabs (5 primary views)
    tab_selection = st.sidebar.radio(
        "Select View:",
        ["💬 Ask", "📊 Investigate", "🚨 Attention Queue", "🔮 Scenario Simulator", "📄 Brief"],
        index=0
    )

    # Render LLM Settings & Spec Compliance Panel
    render_llm_settings_sidebar()
    render_system_compliance_panel(st.session_state["status_info"])

    deals = st.session_state["deals"]
    work_orders = st.session_state["work_orders"]

    st.markdown("---")

    if tab_selection == "💬 Ask":
        render_ask_view(deals, work_orders)
    elif tab_selection == "📊 Investigate":
        render_investigate_view(deals, work_orders)
    elif tab_selection == "🚨 Attention Queue":
        render_attention_view(deals, work_orders)
    elif tab_selection == "🔮 Scenario Simulator":
        render_scenario_view(deals, work_orders)
    elif tab_selection == "📄 Brief":
        render_brief_view(deals, work_orders)
