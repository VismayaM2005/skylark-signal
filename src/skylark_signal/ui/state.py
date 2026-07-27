import streamlit as st
from skylark_signal.config import config
from skylark_signal.data.dashboard_repository import DashboardRepository
from skylark_signal.agent.context import ConversationContext
from skylark_signal.llm.openrouter import fetch_openrouter_models

def init_session_state():
    """Initializes Streamlit session state variables if not already set."""
    if "deals" not in st.session_state or "work_orders" not in st.session_state:
        repo = DashboardRepository()
        deals, work_orders, status_info = repo.load_data()
        st.session_state["deals"] = deals
        st.session_state["work_orders"] = work_orders
        st.session_state["status_info"] = status_info

    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "Ask"
        
    if "current_query" not in st.session_state:
        st.session_state["current_query"] = ""

    if "conversation_context" not in st.session_state:
        st.session_state["conversation_context"] = ConversationContext()

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if "selected_sector" not in st.session_state:
        st.session_state["selected_sector"] = "All Sectors"

    if "selected_owner" not in st.session_state:
        st.session_state["selected_owner"] = "All Owners"

    if "selected_status" not in st.session_state:
        st.session_state["selected_status"] = "All Statuses"

    # LLM Settings Session State
    if "llm_provider" not in st.session_state:
        if config.openrouter_api_key:
            st.session_state["llm_provider"] = "OpenRouter"
        elif config.openai_api_key:
            st.session_state["llm_provider"] = "OpenAI"
        else:
            st.session_state["llm_provider"] = "Deterministic"

    if "openrouter_models" not in st.session_state:
        st.session_state["openrouter_models"] = fetch_openrouter_models()

    if "selected_llm_model" not in st.session_state:
        models = st.session_state["openrouter_models"]
        st.session_state["selected_llm_model"] = models[0].id if models else "openai/gpt-4o-mini"
