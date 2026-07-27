import os, re
from typing import Dict, Any, Optional, Tuple
from skylark_signal.agent.router import route_query_intent
from skylark_signal.agent.prompts import sanitize_query, build_llm_phrasing_prompt, SYSTEM_SAFETY_PROMPT
from skylark_signal.agent.context import ConversationContext, KNOWN_SECTORS
from skylark_signal.llm.client import LLMClient
from skylark_signal.llm.schemas import LLMTrace

class QueryPlanner:
    """
    Query Planner that handles deterministic intent routing, ambiguity detection/clarification,
    and multi-turn conversational phrasing via LLMClient.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def check_ambiguity(
        self,
        query: str,
        context: Optional[ConversationContext] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detects if a user query is materially ambiguous.
        Returns (is_ambiguous, clarification_prompt, missing_dimension).
        """
        cleaned = sanitize_query(query).lower()

        # Check explicit sector presence in query or active context
        sector_mentioned = any(re.search(r'\b' + re.escape(s.lower()) + r'\b', cleaned) for s in KNOWN_SECTORS)
        context_sector = context.active_sector if context else None

        # Scenario 1: Unspecified sector breakdown
        if ("sector" in cleaned or "industry" in cleaned) and not sector_mentioned and not context_sector:
            if "performance" in cleaned or "pipeline" in cleaned or "breakdown" in cleaned:
                return (
                    True,
                    "Which specific sector would you like to analyze (e.g., Mining, Renewables, Powerline, or All Sectors)?",
                    "sector"
                )

        # Scenario 2: Unspecified period comparison
        if "compare" in cleaned and not any(term in cleaned for term in ["quarter", "month", "year", "q1", "q2", "q3", "q4", "last", "previous"]):
            return (
                True,
                "Which comparison time window would you like to evaluate against (e.g., Previous Quarter, Last 60 Days, or Year-to-Date)?",
                "time_period"
            )

        return False, None, None

    def plan_query(self, query: str, context: Optional[ConversationContext] = None) -> Dict[str, Any]:
        """
        Analyzes a user query and returns a structured query plan with ambiguity detection.
        """
        cleaned = sanitize_query(query)
        intent, conf, rule = route_query_intent(cleaned)
        
        is_ambiguous, clar_prompt, missing_dim = self.check_ambiguity(cleaned, context)

        return {
            "raw_query": query,
            "sanitized_query": cleaned,
            "intent": intent,
            "confidence": conf,
            "rule_used": rule,
            "is_ambiguous": is_ambiguous,
            "clarification_prompt": clar_prompt,
            "missing_dimension": missing_dim
        }

    def rephrase_answer_with_trace(
        self,
        query: str,
        executive_answer: str,
        key_metrics: dict,
        provider: str = "deterministic",
        model_slug: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Calls LLMClient to polish executive response if a remote provider is active.
        Returns (final_text, llm_trace_dict).
        """
        provider_clean = (provider or "deterministic").lower().strip()

        if provider_clean == "deterministic":
            trace = LLMTrace(
                provider="Deterministic",
                model_slug="None (Deterministic)",
                used_llm=False,
                execution_path="deterministic",
                fallback_reason="Provider set to Deterministic",
                raw_text=executive_answer
            )
            return executive_answer, trace.model_dump()

        prompt = build_llm_phrasing_prompt(query, executive_answer, key_metrics)
        trace = self.llm_client.generate_text_with_trace(
            prompt=prompt,
            system_prompt=SYSTEM_SAFETY_PROMPT,
            provider=provider,
            model_slug=model_slug
        )

        final_text = trace.raw_text if trace.used_llm and trace.raw_text else executive_answer
        return final_text, trace.model_dump()

    def rephrase_answer(
        self,
        query: str,
        executive_answer: str,
        key_metrics: dict,
        provider: str = "deterministic",
        model_slug: Optional[str] = None
    ) -> str:
        """Convenience backward-compatible wrapper."""
        text, _ = self.rephrase_answer_with_trace(query, executive_answer, key_metrics, provider, model_slug)
        return text
