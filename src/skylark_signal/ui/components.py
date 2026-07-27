import streamlit as st
from skylark_signal.config import config
from skylark_signal.llm.openrouter import fetch_openrouter_models
from skylark_signal.llm.client import LLMClient

def render_data_source_badge(status_info: dict):
    """Renders data source status badge in UI sidebar header."""
    is_live = status_info.get("is_live", False)
    mode_label = status_info.get("mode_label", "Data Source")
    timestamp = status_info.get("timestamp", "")[:19].replace("T", " ")
    
    if is_live:
        st.sidebar.markdown(f"🟢 **Data Source**: `{mode_label}`")
    else:
        st.sidebar.markdown(f"🟡 **Data Source**: `{mode_label}` *(Fallback Mode Active)*")
        st.sidebar.caption("⚠️ *FALLBACK MODE ACTIVE: Using offline processed JSON files (data/processed/). MONDAY_API_TOKEN is unset or connection failed.*")
        
    st.sidebar.caption(f"Last Refreshed: `{timestamp} UTC`")
    st.sidebar.caption(f"Loaded: `{status_info.get('deals_count', 0)} Deals` | `{status_info.get('work_orders_count', 0)} Work Orders`")

def render_system_compliance_panel(status_info: dict, trust_score: float = 79.4):
    """Renders System Compliance & Spec Status panel in UI sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛡️ System Spec Compliance")
    
    is_live = status_info.get("is_live", False)
    provider = st.session_state.get("llm_provider", "Deterministic")
    selected_model = st.session_state.get("selected_llm_model", "none")

    with st.sidebar.expander("📋 Spec Compliance Details", expanded=False):
        st.markdown(f"- **Clarification Support**: `ON`")
        st.markdown(f"- **Conversational Memory**: `ON`")
        st.markdown(f"- **Live monday API Mode**: `{'ON' if is_live else 'OFF'}`")
        st.markdown(f"- **Fallback Mode**: `{'ON (Processed Snapshot)' if not is_live else 'OFF'}`")
        st.markdown(f"- **Selected Provider**: `{provider}`")
        st.markdown(f"- **Active Model**: `{selected_model if provider != 'Deterministic' else 'None (Deterministic)'}`")
        st.markdown(f"- **Data Trust Score**: `{trust_score:.1f} / 100`")

def render_llm_settings_sidebar():
    """Renders the LLM Settings sidebar section with multi-provider model selection, key input, and Test LLM button."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ LLM Settings")

    provider_options = ["Deterministic", "OpenRouter", "OpenAI"]
    curr_provider = st.session_state.get("llm_provider", "Deterministic")
    
    provider_idx = provider_options.index(curr_provider) if curr_provider in provider_options else 0
    sel_provider = st.sidebar.selectbox("Provider", provider_options, index=provider_idx)
    st.session_state["llm_provider"] = sel_provider

    sel_slug = None

    if sel_provider == "OpenRouter":
        custom_key = st.sidebar.text_input(
            "Paste OpenRouter API Key:",
            value=st.session_state.get("user_openrouter_key", config.openrouter_api_key or ""),
            type="password",
            help="Paste your sk-or-v1-... key here or set OPENROUTER_API_KEY in .env"
        )
        if custom_key:
            config.openrouter_api_key = custom_key
            st.session_state["user_openrouter_key"] = custom_key

        if config.openrouter_api_key:
            st.sidebar.markdown(f"🟢 **OpenRouter Key**: `{config.masked_openrouter_token}`")
        else:
            st.sidebar.markdown("🟡 **OpenRouter Key**: `UNSET (Deterministic Fallback)`")

        models = st.session_state.get("openrouter_models", [])
        if st.sidebar.button("🔄 Refresh Models"):
            models = fetch_openrouter_models(api_key=config.openrouter_api_key, force_refresh=True)
            st.session_state["openrouter_models"] = models
            st.sidebar.success("✓ Model list refreshed!")

        model_slugs = [m.id for m in models]
        model_labels = [f"{m.name} ({m.id})" for m in models]

        curr_model = st.session_state.get("selected_llm_model", model_slugs[0] if model_slugs else "openai/gpt-4o-mini")
        model_idx = model_slugs.index(curr_model) if curr_model in model_slugs else 0

        sel_label = st.sidebar.selectbox("Select Model", model_labels, index=model_idx)
        sel_slug = model_slugs[model_labels.index(sel_label)]
        st.session_state["selected_llm_model"] = sel_slug

    elif sel_provider == "OpenAI":
        custom_key = st.sidebar.text_input(
            "Paste OpenAI API Key:",
            value=st.session_state.get("user_openai_key", config.openai_api_key or ""),
            type="password",
            help="Paste your sk-... key here or set OPENAI_API_KEY in .env"
        )
        if custom_key:
            config.openai_api_key = custom_key
            st.session_state["user_openai_key"] = custom_key

        if config.openai_api_key:
            st.sidebar.markdown("🟢 **OpenAI Key**: `SET`")
        else:
            st.sidebar.markdown("🟡 **OpenAI Key**: `UNSET (Deterministic Fallback)`")

        sel_slug = st.sidebar.selectbox(
            "Select OpenAI Model",
            ["gpt-4o-mini", "gpt-4o"],
            index=0
        )
        st.session_state["selected_llm_model"] = sel_slug
    else:
        st.sidebar.markdown("🔒 **Mode**: `100% Deterministic (No LLM)`")
        sel_slug = "none"

    # Test LLM Button
    if sel_provider != "Deterministic":
        if st.sidebar.button("⚡ Test LLM Connection"):
            with st.sidebar.spinner("Testing API connection..."):
                client = LLMClient()
                test_prompt = f"Reply with the word READY and the model name: {sel_slug}"
                trace = client.generate_text_with_trace(
                    prompt=test_prompt,
                    provider=sel_provider,
                    model_slug=sel_slug
                )
                if trace.used_llm:
                    st.sidebar.success(f"✓ LLM Connected!\n\n**Output**: `{trace.raw_text}`")
                else:
                    st.sidebar.error(f"❌ Fallback Triggered:\n\n`{trace.fallback_reason}`")

    st.sidebar.caption("💡 *Note: Analytics remain 100% deterministic Python calculations. LLM is used only for Ask view phrasing.*")

def render_status_badge(overall_status: str):
    """Renders large business status badge."""
    if overall_status == "GREEN":
        st.markdown("<span style='background-color:#1E4620; color:#4EFE84; padding:6px 14px; border-radius:16px; font-weight:bold; font-size:14px;'>🟢 BUSINESS HEALTH: GREEN</span>", unsafe_allow_html=True)
    elif overall_status == "AMBER":
        st.markdown("<span style='background-color:#4E3800; color:#FFD166; padding:6px 14px; border-radius:16px; font-weight:bold; font-size:14px;'>🟡 BUSINESS HEALTH: AMBER</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='background-color:#4A151B; color:#FF6B6B; padding:6px 14px; border-radius:16px; font-weight:bold; font-size:14px;'>🔴 BUSINESS HEALTH: RED</span>", unsafe_allow_html=True)

def render_trust_badge(score: float, rating: str):
    """Renders data trust score indicator."""
    st.markdown(f"🔒 **Data Trust Score**: `{score:.1f}/100` — **{rating}**")

def render_metric_card(label: str, value: str, caption: str = None):
    """Renders clean executive metric card."""
    with st.container():
        st.metric(label=label, value=value)
        if caption:
            st.caption(caption)
