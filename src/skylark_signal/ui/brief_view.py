import streamlit as st
from typing import List, Any
from skylark_signal.ui.components import render_status_badge, render_trust_badge
from skylark_signal.ui.downloaders import render_download_buttons
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.reporting import format_leadership_brief_markdown

def render_brief_view(deals: List[Any], work_orders: List[Any]):
    """Renders the one-click Brief view for founder leadership updates."""
    st.markdown("### 📄 Founder Leadership Brief")
    st.caption("Copy-ready executive summary generated deterministically from live board metrics.")

    bundle = build_full_analytics_bundle(deals, work_orders)
    brief = bundle["leadership_brief"]
    trust = bundle["data_trust_score"]

    st.markdown("---")
    # 1. Status Badge & Executive Pulse
    render_status_badge(brief["overall_status"])
    st.markdown(f"**Generated**: `{brief['generation_timestamp'][:19].replace('T', ' ')} UTC`")

    st.markdown("#### 💡 Executive Pulse")
    st.info(brief["executive_pulse"])

    st.markdown("---")
    # 2. Five Numbers to Quote
    st.markdown("#### 🔢 Five Numbers to Quote")
    cols = st.columns(5)
    for idx, num in enumerate(brief["five_numbers_to_quote"]):
        with cols[idx]:
            st.metric(label=num["label"], value=num["value"])

    st.markdown("---")
    # 3. Top Wins & Top Risks
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🏆 Top Wins & Strengths")
        for win in brief["top_wins"]:
            st.success(f"✓ {win}")
    with c2:
        st.markdown("#### ⚠️ Top Risks & Bottlenecks")
        for risk in brief["top_risks"]:
            st.error(f"⚠️ {risk}")

    st.markdown("---")
    # 4. Decisions Required & Recommended Actions
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 📌 Decisions Required")
        for dec in brief["decisions_required"]:
            st.markdown(f"1. {dec}")
    with c4:
        st.markdown("#### 📋 Recommended Actions")
        for act in brief["recommended_actions"]:
            st.markdown(f"- [ ] {act}")

    st.markdown("---")
    # 5. Data Trust Indicator
    render_trust_badge(trust["combined_trust_score"], trust["trust_rating"])

    st.markdown("---")
    # 6. Download Buttons
    render_download_buttons(bundle)
