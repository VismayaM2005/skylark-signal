import streamlit as st
from skylark_signal.config import config
from skylark_signal.llm.openrouter import fetch_openrouter_models
from skylark_signal.llm.client import LLMClient


def render_hero_banner(status_info: dict, trust_score: float = 79.4):
    """Renders premium product hero section with live status pills and trust score."""
    is_live = status_info.get("is_live", False)
    mode_label = status_info.get("mode_label", "Data Source")
    provider = st.session_state.get("llm_provider", "Deterministic")
    selected_model = st.session_state.get("selected_llm_model", "none")
    deals_count = status_info.get("deals_count", 0)
    wo_count = status_info.get("work_orders_count", 0)

    source_pill_html = (
        f'<span class="pill-live">LIVE MONDAY API · {mode_label}</span>'
        if is_live
        else f'<span class="pill-fallback">⚠ FALLBACK SNAPSHOT · {mode_label}</span>'
    )

    trust_pill_html = f'<span class="pill-trust">🔒 Trust Score: {trust_score:.0f}/100</span>'
    provider_pill_html = (
        f'<span class="pill-provider">🤖 {provider}'
        + (f' · {selected_model.split("/")[-1] if "/" in selected_model else selected_model}' if provider != "Deterministic" else "")
        + '</span>'
    )
    records_pill_html = f'<span class="pill-provider">📊 {deals_count} Deals · {wo_count} Work Orders</span>'

    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-eyebrow">✦ Founder Intelligence Platform</div>
            <div class="hero-wordmark">Skylark <span class="accent">Signal</span></div>
            <div class="hero-tagline">
                Real-time business intelligence across monday.com Deals &amp; Work Orders — deterministic, auditable, boardroom-ready.
            </div>
            <div class="hero-pills">
                {source_pill_html}
                {trust_pill_html}
                {provider_pill_html}
                {records_pill_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_source_badge(status_info: dict):
    """Renders data source status badge in the sidebar."""
    is_live = status_info.get("is_live", False)
    mode_label = status_info.get("mode_label", "Data Source")
    timestamp = status_info.get("timestamp", "")[:19].replace("T", " ")

    if is_live:
        st.sidebar.markdown(
            f"<div style='padding:8px 12px; background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:10px; margin-bottom:8px;'>"
            f"<span style='color:#34D399; font-weight:700; font-size:12px;'>● LIVE API</span> "
            f"<span style='color:#64748B; font-size:11px;'>· {mode_label}</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            f"<div style='padding:8px 12px; background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2); border-radius:10px; margin-bottom:4px;'>"
            f"<span style='color:#FBBF24; font-weight:700; font-size:12px;'>⚠ FALLBACK</span> "
            f"<span style='color:#64748B; font-size:11px;'>· {mode_label}</span></div>",
            unsafe_allow_html=True,
        )
        st.sidebar.caption("Set MONDAY_API_TOKEN to enable live data.")

    st.sidebar.caption(f"Refreshed: `{timestamp} UTC`")
    st.sidebar.caption(
        f"Loaded: `{status_info.get('deals_count', 0)}` deals · `{status_info.get('work_orders_count', 0)}` work orders"
    )


def render_system_compliance_panel(status_info: dict, trust_score: float = 79.4):
    """Renders Spec Compliance audit panel in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<span style='font-size:12px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.8px;'>🛡 Spec Compliance</span>",
        unsafe_allow_html=True,
    )

    is_live = status_info.get("is_live", False)
    provider = st.session_state.get("llm_provider", "Deterministic")
    selected_model = st.session_state.get("selected_llm_model", "none")

    def _check(label: str, on: bool):
        icon = "✓" if on else "✗"
        color = "#34D399" if on else "#EF4444"
        val = "ON" if on else "OFF"
        st.sidebar.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:3px 0;font-size:12px;'>"
            f"<span style='color:#94A3B8;'>{label}</span>"
            f"<span style='color:{color};font-weight:700;'>{icon} {val}</span></div>",
            unsafe_allow_html=True,
        )

    with st.sidebar.expander("📋 Audit Details", expanded=False):
        _check("Clarification Engine", True)
        _check("Conversational Memory", True)
        _check("Live Monday API", is_live)
        _check("Fallback Mode", not is_live)
        st.markdown(
            f"<div style='margin-top:8px; padding-top:8px; border-top:1px solid rgba(56,189,248,0.08); font-size:11px; color:#475569;'>"
            f"Provider: <b style='color:#94A3B8'>{provider}</b><br>"
            f"Model: <b style='color:#94A3B8'>{selected_model if provider != 'Deterministic' else '—'}</b><br>"
            f"Trust Score: <b style='color:#A5B4FC'>{trust_score:.1f} / 100</b></div>",
            unsafe_allow_html=True,
        )


def render_llm_settings_sidebar():
    """Renders the LLM Settings sidebar panel with provider & model selection."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<span style='font-size:12px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.8px;'>⚙ LLM Settings</span>",
        unsafe_allow_html=True,
    )

    provider_options = ["Deterministic", "OpenRouter", "OpenAI"]
    curr_provider = st.session_state.get("llm_provider", "Deterministic")
    provider_idx = provider_options.index(curr_provider) if curr_provider in provider_options else 0
    sel_provider = st.sidebar.selectbox("Provider", provider_options, index=provider_idx)
    st.session_state["llm_provider"] = sel_provider

    sel_slug = None

    if sel_provider == "OpenRouter":
        custom_key = st.sidebar.text_input(
            "OpenRouter API Key:",
            value=st.session_state.get("user_openrouter_key", config.openrouter_api_key or ""),
            type="password",
            help="Paste sk-or-v1-... key or set OPENROUTER_API_KEY in .env",
        )
        if custom_key:
            config.openrouter_api_key = custom_key
            st.session_state["user_openrouter_key"] = custom_key

        if config.openrouter_api_key:
            st.sidebar.markdown(f"<span style='color:#34D399; font-size:12px;'>● Key set: `{config.masked_openrouter_token}`</span>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown("<span style='color:#FBBF24; font-size:12px;'>⚠ Key unset — deterministic fallback</span>", unsafe_allow_html=True)

        models = st.session_state.get("openrouter_models", [])
        if st.sidebar.button("🔄 Refresh Models"):
            models = fetch_openrouter_models(api_key=config.openrouter_api_key, force_refresh=True)
            st.session_state["openrouter_models"] = models
            st.sidebar.success("✓ Models refreshed!")

        model_slugs = [m.id for m in models]
        model_labels = [f"{m.name} ({m.id})" for m in models]
        curr_model = st.session_state.get("selected_llm_model", model_slugs[0] if model_slugs else "openai/gpt-4o-mini")
        model_idx = model_slugs.index(curr_model) if curr_model in model_slugs else 0
        sel_label = st.sidebar.selectbox("Model", model_labels, index=model_idx)
        sel_slug = model_slugs[model_labels.index(sel_label)]
        st.session_state["selected_llm_model"] = sel_slug

    elif sel_provider == "OpenAI":
        custom_key = st.sidebar.text_input(
            "OpenAI API Key:",
            value=st.session_state.get("user_openai_key", config.openai_api_key or ""),
            type="password",
            help="Paste sk-... key or set OPENAI_API_KEY in .env",
        )
        if custom_key:
            config.openai_api_key = custom_key
            st.session_state["user_openai_key"] = custom_key

        if config.openai_api_key:
            st.sidebar.markdown("<span style='color:#34D399; font-size:12px;'>● OpenAI key set</span>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown("<span style='color:#FBBF24; font-size:12px;'>⚠ Key unset — deterministic fallback</span>", unsafe_allow_html=True)

        sel_slug = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
        st.session_state["selected_llm_model"] = sel_slug

    else:
        st.sidebar.markdown(
            "<div style='padding:8px 12px; background:rgba(56,189,248,0.06); border:1px solid rgba(56,189,248,0.12); border-radius:8px; font-size:12px; color:#38BDF8;'>🔒 100% Deterministic — No LLM calls</div>",
            unsafe_allow_html=True,
        )
        sel_slug = "none"

    if sel_provider != "Deterministic":
        if st.sidebar.button("⚡ Test LLM Connection"):
            with st.sidebar.spinner("Testing connection…"):
                client = LLMClient()
                trace = client.generate_text_with_trace(
                    prompt=f"Reply READY and model: {sel_slug}",
                    provider=sel_provider,
                    model_slug=sel_slug,
                )
                if trace.used_llm:
                    st.sidebar.success(f"✓ Connected!\n\n`{trace.raw_text}`")
                else:
                    st.sidebar.error(f"❌ Fallback: `{trace.fallback_reason}`")

    st.sidebar.caption("💡 Analytics are always 100% deterministic. LLM only phrases Ask-view answers.")


def render_status_badge(overall_status: str):
    """Renders premium business health status badge."""
    if overall_status == "GREEN":
        st.markdown(
            "<span class='status-green'>● BUSINESS HEALTH: GREEN</span>",
            unsafe_allow_html=True,
        )
    elif overall_status == "AMBER":
        st.markdown(
            "<span class='status-amber'>● BUSINESS HEALTH: AMBER</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='status-red'>● BUSINESS HEALTH: RED</span>",
            unsafe_allow_html=True,
        )


def render_trust_badge(score: float, rating: str):
    """Renders premium data trust score with progress bar."""
    bar_width = max(0, min(100, score))
    st.markdown(
        f"""
        <div class="trust-badge">
            🔒 Data Trust Score:
            <span style="color:#E2E8F0; font-weight:800;">{score:.1f} / 100</span>
            &nbsp;—&nbsp;
            <span style="color:#94A3B8;">{rating}</span>
        </div>
        <div class="trust-bar-track" style="width:100%; max-width:300px; margin-top:6px;">
            <div class="trust-bar-fill" style="width:{bar_width}%;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, caption: str = None):
    """Renders clean executive metric card."""
    st.metric(label=label, value=value)
    if caption:
        st.caption(caption)


def render_view_header(title: str, subtitle: str):
    """Renders a consistent, premium view header."""
    st.markdown(
        f"""
        <div class="view-header">
            <div class="view-title">{title}</div>
            <div class="view-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
