import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from unittest.mock import MagicMock
from skylark_signal.agent.planner import QueryPlanner
from skylark_signal.llm.schemas import LLMTrace

def test_query_planner_deterministic():
    planner = QueryPlanner()
    plan = planner.plan_query("What requires my attention right now?")

    assert plan["intent"] == "founder_attention"
    assert plan["confidence"] >= 0.90

def test_query_planner_rephrase_fallback_without_key():
    planner = QueryPlanner()
    raw_ans = "Total open pipeline is 500,000 INR."
    rephrased = planner.rephrase_answer("How is pipeline?", raw_ans, {}, provider="deterministic")

    assert rephrased == raw_ans

def test_query_planner_rephrase_with_mock_client():
    mock_client = MagicMock()
    mock_client.generate_text_with_trace.return_value = LLMTrace(
        provider="OpenRouter",
        model_slug="anthropic/claude-3.5-sonnet",
        used_llm=True,
        execution_path="openrouter",
        fallback_reason=None,
        raw_text="Polished LLM response."
    )
    
    planner = QueryPlanner(llm_client=mock_client)
    raw_ans = "Total open pipeline is 500,000 INR."
    rephrased = planner.rephrase_answer("How is pipeline?", raw_ans, {}, provider="openrouter", model_slug="anthropic/claude-3.5-sonnet")

    assert rephrased == "Polished LLM response."
    assert mock_client.generate_text_with_trace.call_count == 1
