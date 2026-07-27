import streamlit as st
from skylark_signal.ui.styles import inject_custom_styles
from skylark_signal.ui.state import init_session_state
from skylark_signal.ui.components import (
    render_hero_banner,
    render_data_source_badge,
    render_llm_settings_sidebar,
    render_system_compliance_panel,
)
from skylark_signal.ui.ask_view import render_ask_view
from skylark_signal.ui.investigate_view import render_investigate_view
from skylark_signal.ui.attention_view import render_attention_view
from skylark_signal.ui.scenario_view import render_scenario_view
from skylark_signal.ui.brief_view import render_brief_view
from skylark_signal.ui.status_view import render_status_view
from skylark_signal.data.dashboard_repository import DashboardRepository


NAV_ITEMS = [
    ("💬", "Ask",                    "Ask Skylark Signal"),
    ("📊", "Investigate",            "Visual Dashboard"),
    ("📄", "Leadership Brief",       "Executive Memo"),
    ("🔮", "Scenario Simulator",     "What-If Engine"),
    ("🚨", "Attention Queue",        "Founder Action Items"),
    ("🛡️", "System Status",         "Platform Health"),
]


def run_app_shell():
    """Renders the main Skylark Signal app shell: custom CSS, hero banner, 6-view navigation, sidebar controls."""
    st.set_page_config(
        page_title="Skylark Signal — Founder Decision Cockpit",
        page_icon="🦅",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_custom_styles()
    init_session_state()

    status_info = st.session_state["status_info"]
    deals = st.session_state["deals"]
    work_orders = st.session_state["work_orders"]

    # ── Hero Banner ────────────────────────────────────────────
    render_hero_banner(status_info, trust_score=79.4)

    # ── Sidebar ────────────────────────────────────────────────
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; padding:4px 0 16px 0; border-bottom:1px solid rgba(56,189,248,0.08); margin-bottom:16px;">
            <span style="font-size:28px;">🦅</span>
            <div>
                <div style="font-weight:800; font-size:16px; color:#F0F8FF; letter-spacing:-0.5px;">Skylark Signal</div>
                <div style="font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:0.8px;">Founder Cockpit</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_data_source_badge(status_info)

    # Manual Refresh
    if st.sidebar.button("🔄 Refresh Board Data"):
        repo = DashboardRepository()
        deals, work_orders, status_info = repo.load_data()
        st.session_state["deals"] = deals
        st.session_state["work_orders"] = work_orders
        st.session_state["status_info"] = status_info
        st.sidebar.success("✓ Board data refreshed!")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<span style='font-size:12px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.8px;'>Navigation</span>",
        unsafe_allow_html=True,
    )

    # Navigation using radio
    nav_labels = [f"{icon} {name}" for icon, name, _ in NAV_ITEMS]
    tab_selection = st.sidebar.radio(
        "View:",
        nav_labels,
        index=0,
        label_visibility="collapsed",
    )

    render_llm_settings_sidebar()
    render_system_compliance_panel(status_info)

    # ── Main Content ───────────────────────────────────────────
    if "💬" in tab_selection:
        render_ask_view(deals, work_orders)
    elif "📊" in tab_selection:
        render_investigate_view(deals, work_orders)
    elif "📄" in tab_selection:
        render_brief_view(deals, work_orders)
    elif "🔮" in tab_selection:
        render_scenario_view(deals, work_orders)
    elif "🚨" in tab_selection:
        render_attention_view(deals, work_orders)
    elif "🛡️" in tab_selection:
        render_status_view(deals, work_orders)
