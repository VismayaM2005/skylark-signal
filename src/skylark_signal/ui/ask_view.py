import streamlit as st
from typing import List, Any
from skylark_signal.agent import SafeExecutiveResponder
from skylark_signal.ui.components import render_trust_badge

def render_ask_view(deals: List[Any], work_orders: List[Any]):
    """Renders the conversational Ask view for founder queries with multi-turn context memory & ambiguity clarification."""
    st.markdown("### 💬 Ask Skylark Signal")
    st.caption("Ask any founder-level business query. Answers are computed deterministically from verified board data.")

    # Active Provider, Model Choice, and Conversational Context Info
    provider = st.session_state.get("llm_provider", "Deterministic")
    selected_model = st.session_state.get("selected_llm_model", "openai/gpt-4o-mini")
    context = st.session_state.get("conversation_context")

    c_info1, c_info2 = st.columns([3, 1])
    with c_info1:
        st.caption(
            f"🤖 Active Agent Mode: `{provider}` | Model: `{selected_model if provider != 'Deterministic' else 'None (Deterministic)'}`"
            f"{f' | Active Context Sector: **{context.active_sector}**' if context and context.active_sector else ''}"
        )
    with c_info2:
        if context and context.turns_count > 0:
            if st.button("🧹 Clear Chat Context"):
                context.clear()
                st.session_state["current_query"] = ""
                st.session_state["chat_history"] = []
                st.rerun()

    # Starter Question Prompts
    st.markdown("**Suggested Founder Queries:**")
    col1, col2, col3, col4 = st.columns(4)
    
    starter_query = None
    with col1:
        if st.button("⚡ What requires attention?"):
            starter_query = "What requires my attention right now?"
    with col2:
        if st.button("⚠️ How much revenue is at risk?"):
            starter_query = "How much revenue is at risk?"
    with col3:
        if st.button("⏳ Which deals are stale?"):
            starter_query = "Which deals are stale?"
    with col4:
        if st.button("💼 What to discuss in leadership?"):
            starter_query = "What should I discuss in the next leadership meeting?"

    # Query Input Box
    user_query = st.text_input(
        "Enter your query:",
        value=starter_query if starter_query else st.session_state.get("current_query", ""),
        placeholder="e.g. How is the Mining pipeline looking this quarter?"
    )

    if user_query:
        st.session_state["current_query"] = user_query
        responder = SafeExecutiveResponder()
        response = responder.respond(
            query=user_query,
            deals=deals,
            work_orders=work_orders,
            provider=provider,
            model_slug=selected_model,
            context=context
        )

        trace = response.get("llm_trace", {})

        st.markdown("---")

        # Fallback Warning Banner if OpenRouter/OpenAI was requested but deterministic mode was used
        if provider != "Deterministic" and not trace.get("used_llm", False):
            st.warning(
                f"⚠️ **Warning**: `{provider}` was selected, but execution fell back to **Deterministic mode** "
                f"because: `{trace.get('fallback_reason', 'API key missing or request failed')}`. "
                "Please check your API key in LLM Settings."
            )

        # Handle Clarification Required
        if response.get("is_clarification", False):
            st.warning(response["executive_answer"])
        else:
            # 1. Executive Answer
            st.markdown("#### 💡 Executive Answer")
            st.info(response["executive_answer"])

        # 2. Key Metrics Cards
        st.markdown("#### 📊 Key Metrics")
        k_cols = st.columns(len(response["key_metrics"]))
        for idx, (k, v) in enumerate(response["key_metrics"].items()):
            with k_cols[idx]:
                st.metric(label=k, value=str(v))

        # 3. Business Interpretation & 4. Recommended Actions
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🎯 Why This Matters")
            st.write(response["business_interpretation"])
        with c2:
            st.markdown("#### 📋 Recommended Actions")
            for act in response["recommended_actions"]:
                st.markdown(f"- [ ] {act}")

        # 5. Data Trust Score & 6. Data Caveats
        st.markdown("---")
        t_score = response["data_trust_score"]["score"]
        t_rating = response["data_trust_score"]["rating"]
        render_trust_badge(t_score, t_rating)

        if response["data_caveats"]:
            with st.expander("📌 Data Caveats & Missing Fields"):
                for cav in response["data_caveats"]:
                    st.caption(f"• {cav}")

        # 7. LLM Execution Trace & Proof Block
        with st.expander("🤖 LLM Execution Trace & Proof (Debug Info)"):
            st.json({
                "requested_provider": trace.get("provider"),
                "requested_model_slug": trace.get("model_slug"),
                "used_llm": trace.get("used_llm"),
                "execution_path": trace.get("execution_path"),
                "fallback_reason": trace.get("fallback_reason"),
                "active_context_sector": context.active_sector if context else None,
                "context_turns_count": context.turns_count if context else 0
            })

        # 8. Evidence & Formulas
        if response["evidence_and_formulas"]:
            with st.expander("🔍 Evidence & Calculation Formulas"):
                for f_item in response["evidence_and_formulas"]:
                    st.code(f_item, language="text")

        # 9. Expandable Source Records
        with st.expander("📂 View Sample Source Records"):
            st.caption("Showing first 5 underlying canonical deal/work order records:")
            sample_deals = [{"Deal ID": d.deal_id, "Name": d.deal_name, "Customer": d.customer, "Stage": d.stage, "Value": d.deal_value} for d in deals[:5]]
            st.dataframe(sample_deals, use_container_width=True)

        # 10. Suggested Follow-Up Questions
        if response["suggested_followups"]:
            st.markdown("#### 💡 Suggested Follow-up Queries")
            f_cols = st.columns(len(response["suggested_followups"]))
            for idx, f_q in enumerate(response["suggested_followups"]):
                with f_cols[idx]:
                    if st.button(f"👉 {f_q}", key=f"followup_{idx}"):
                        st.session_state["current_query"] = f_q
                        st.rerun()
