import streamlit as st
from typing import List, Any
from skylark_signal.agent import SafeExecutiveResponder
from skylark_signal.ui.components import render_trust_badge, render_view_header


_STARTER_QUERIES = [
    ("⚡", "What requires attention?",        "What requires my attention right now?"),
    ("⚠️", "Revenue at risk?",                "How much revenue is at risk?"),
    ("⏳", "Which deals are stale?",          "Which deals are stale and need follow-up?"),
    ("💼", "Leadership talking points?",      "What should I discuss in the next leadership meeting?"),
]


def render_ask_view(deals: List[Any], work_orders: List[Any]):
    """Renders the conversational Ask view with multi-turn context, clarification engine, and premium response cards."""
    render_view_header(
        "💬 Ask Skylark Signal",
        "Natural-language founder queries answered deterministically from live board data.",
    )

    provider = st.session_state.get("llm_provider", "Deterministic")
    selected_model = st.session_state.get("selected_llm_model", "openai/gpt-4o-mini")
    context = st.session_state.get("conversation_context")

    # ── Context Status Bar ────────────────────────────────────
    ctx_parts = []
    ctx_parts.append(
        f"<span style='color:#475569;'>Mode:</span> <span style='color:#38BDF8; font-weight:600;'>{provider}</span>"
    )
    if provider != "Deterministic":
        model_short = selected_model.split("/")[-1] if "/" in selected_model else selected_model
        ctx_parts.append(
            f"<span style='color:#475569;'>Model:</span> <span style='color:#94A3B8; font-weight:500;'>{model_short}</span>"
        )
    if context and context.active_sector:
        ctx_parts.append(
            f"<span style='color:#475569;'>Context Sector:</span> <span style='color:#A5B4FC; font-weight:600;'>{context.active_sector}</span>"
        )

    bar_col, clear_col = st.columns([5, 1])
    with bar_col:
        st.markdown(
            "<div style='font-size:12px; padding:6px 0; display:flex; gap:18px; flex-wrap:wrap;'>"
            + " · ".join(ctx_parts)
            + "</div>",
            unsafe_allow_html=True,
        )
    with clear_col:
        if context and context.turns_count > 0:
            if st.button("🧹 Clear", key="clear_ctx"):
                context.clear()
                st.session_state["current_query"] = ""
                st.session_state["chat_history"] = []
                st.rerun()

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ── Starter Query Chips ───────────────────────────────────
    st.markdown(
        "<div style='font-size:12px; font-weight:600; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>Suggested Queries</div>",
        unsafe_allow_html=True,
    )
    chip_cols = st.columns(len(_STARTER_QUERIES))
    starter_query = None
    for idx, (icon, label, full_query) in enumerate(_STARTER_QUERIES):
        with chip_cols[idx]:
            if st.button(f"{icon} {label}", key=f"chip_{idx}"):
                starter_query = full_query

    # ── Query Input ───────────────────────────────────────────
    user_query = st.text_input(
        "Query:",
        value=starter_query if starter_query else st.session_state.get("current_query", ""),
        placeholder="e.g. How is the Mining pipeline looking this quarter?",
        label_visibility="collapsed",
    )

    if not user_query:
        st.markdown(
            """
            <div style="margin-top:32px; text-align:center; padding:48px 24px; border:1px dashed rgba(56,189,248,0.1); border-radius:16px; color:#334155;">
                <div style="font-size:32px; margin-bottom:12px;">🦅</div>
                <div style="font-size:16px; font-weight:600; color:#475569; margin-bottom:6px;">Ready for your query</div>
                <div style="font-size:13px; color:#334155;">Select a suggested query above or type your own founder-level question.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Execute Query ─────────────────────────────────────────
    st.session_state["current_query"] = user_query
    with st.spinner("Analyzing board data…"):
        responder = SafeExecutiveResponder()
        response = responder.respond(
            query=user_query,
            deals=deals,
            work_orders=work_orders,
            provider=provider,
            model_slug=selected_model,
            context=context,
        )

    trace = response.get("llm_trace", {})

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Fallback Warning
    if provider != "Deterministic" and not trace.get("used_llm", False):
        st.markdown(
            f"""
            <div style="padding:12px 16px; background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2); border-radius:12px; margin-bottom:14px; font-size:13px; color:#FBBF24;">
                ⚠ <b>{provider}</b> requested but fell back to deterministic: <code>{trace.get('fallback_reason', 'API key missing')}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Clarification Card ────────────────────────────────────
    if response.get("is_clarification", False):
        st.markdown(
            f"""
            <div class="card-clarification">
                <div style="font-size:12px; font-weight:700; color:#F59E0B; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;">
                    🤔 Clarification Needed
                </div>
                <div style="font-size:15px; color:#FDE68A; line-height:1.6;">
                    {response["executive_answer"].replace("Clarification Required:", "").strip()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # ── Executive Answer Card ─────────────────────────────
        st.markdown(
            f"""
            <div class="card-info" style="margin-bottom:20px;">
                <div style="font-size:11px; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">
                    💡 Executive Answer
                </div>
                <div style="font-size:15px; color:#BAE6FD; line-height:1.7;">
                    {response["executive_answer"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Key Metrics Strip ─────────────────────────────────────
    metrics = response.get("key_metrics", {})
    if metrics:
        st.markdown(
            "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px;'>📊 Key Metrics</div>",
            unsafe_allow_html=True,
        )
        k_cols = st.columns(max(1, min(len(metrics), 5)))
        for idx, (k, v) in enumerate(list(metrics.items())[:5]):
            with k_cols[idx]:
                st.metric(label=k, value=str(v))

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ── Interpretation & Actions ──────────────────────────────
    if not response.get("is_clarification", False):
        interp_col, action_col = st.columns(2)

        with interp_col:
            st.markdown(
                f"""
                <div class="saas-card">
                    <div style="font-size:11px; font-weight:700; color:#34D399; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">
                        🎯 Why This Matters
                    </div>
                    <div style="font-size:14px; color:#CBD5E1; line-height:1.7;">
                        {response.get("business_interpretation", "—")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with action_col:
            actions_html = "".join(
                f'<div style="padding:8px 12px; margin-bottom:8px; background:rgba(56,189,248,0.04); border:1px solid rgba(56,189,248,0.1); border-radius:8px; font-size:13px; color:#94A3B8;">'
                f'<span style="color:#38BDF8; margin-right:8px;">→</span>{act}</div>'
                for act in response.get("recommended_actions", [])
            )
            st.markdown(
                f"""
                <div class="saas-card">
                    <div style="font-size:11px; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">
                        📋 Recommended Actions
                        <span style="margin-left:6px; font-size:10px; color:#334155; font-weight:400; background:rgba(56,189,248,0.06); padding:2px 7px; border-radius:4px; border:1px solid rgba(56,189,248,0.1);">Read-only indicators</span>
                    </div>
                    {actions_html if actions_html else '<span style="color:#334155; font-size:13px;">No actions flagged.</span>'}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Trust Score ───────────────────────────────────────────
    t_score = response["data_trust_score"]["score"]
    t_rating = response["data_trust_score"]["rating"]
    render_trust_badge(t_score, t_rating)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Data Caveats ──────────────────────────────────────────
    if response.get("data_caveats"):
        with st.expander("📌 Data Caveats & Missing Fields"):
            for cav in response["data_caveats"]:
                st.markdown(f"<span style='color:#64748B; font-size:13px;'>• {cav}</span>", unsafe_allow_html=True)

    # ── LLM Execution Trace ───────────────────────────────────
    with st.expander("🤖 LLM Execution Trace (Debug)"):
        st.json(
            {
                "requested_provider": trace.get("provider"),
                "model_slug": trace.get("model_slug"),
                "used_llm": trace.get("used_llm"),
                "execution_path": trace.get("execution_path"),
                "fallback_reason": trace.get("fallback_reason"),
                "active_context_sector": context.active_sector if context else None,
                "context_turns": context.turns_count if context else 0,
            }
        )

    # ── Evidence & Formulas ───────────────────────────────────
    if response.get("evidence_and_formulas"):
        with st.expander("🔍 Evidence & Calculation Formulas"):
            for f_item in response["evidence_and_formulas"]:
                st.code(f_item, language="text")

    # ── Source Records ────────────────────────────────────────
    with st.expander("📂 Sample Source Records"):
        st.caption("First 5 canonical deal records:")
        sample = [
            {"Deal ID": d.deal_id, "Name": d.deal_name, "Customer": d.customer, "Stage": d.stage, "Value": d.deal_value}
            for d in deals[:5]
        ]
        st.dataframe(sample, use_container_width=True)

    # ── Suggested Follow-ups ──────────────────────────────────
    followups = response.get("suggested_followups", [])
    if followups:
        st.markdown(
            "<div style='font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.8px; margin:16px 0 10px 0;'>💡 Suggested Follow-ups</div>",
            unsafe_allow_html=True,
        )
        f_cols = st.columns(len(followups))
        for idx, f_q in enumerate(followups):
            with f_cols[idx]:
                if st.button(f"→ {f_q}", key=f"followup_{idx}"):
                    st.session_state["current_query"] = f_q
                    st.rerun()
