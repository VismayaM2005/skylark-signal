import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from unittest.mock import patch, MagicMock
from skylark_signal.llm.client import LLMClient
from skylark_signal.agent.planner import QueryPlanner
from skylark_signal.agent.responder import SafeExecutiveResponder
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord

def test_llm_trace_metadata_generation():
    client = LLMClient()
    trace = client.generate_text_with_trace("Test prompt", provider="deterministic")

    assert trace.used_llm is False
    assert trace.execution_path == "deterministic"
    assert trace.fallback_reason is not None
    assert trace.provider == "Deterministic"

@patch("requests.post")
def test_llm_trace_openrouter_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "READY: anthropic/claude-3.5-sonnet"}}]
    }
    mock_post.return_value = mock_resp

    client = LLMClient(openrouter_key="sk-or-v1-testkey")
    trace = client.generate_text_with_trace(
        prompt="Reply with the word READY and the model name",
        provider="OpenRouter",
        model_slug="anthropic/claude-3.5-sonnet"
    )

    assert trace.used_llm is True
    assert trace.execution_path == "openrouter"
    assert trace.fallback_reason is None
    assert "READY" in trace.raw_text

def test_openrouter_fallback_warning_in_responder():
    deals = [
        CanonicalDealRecord(
            source_system="Test", source_file="d.xlsx", source_sheet="D", source_row_number=1,
            source_record_id="D1", deal_id="DEAL-001", deal_name="Alpha", customer="C1",
            stage="A. Lead Generated", status="Open", deal_value=100000.0
        )
    ]
    work_orders = []

    # Responder called with OpenRouter but NO API key set -> fallback triggered
    responder = SafeExecutiveResponder()
    response = responder.respond(
        query="What requires attention?",
        deals=deals,
        work_orders=work_orders,
        provider="OpenRouter",
        model_slug="openai/gpt-4o-mini"
    )

    assert "llm_trace" in response
    trace = response["llm_trace"]
    assert trace["provider"] == "OpenRouter"
    assert trace["used_llm"] is False
    assert trace["execution_path"] == "deterministic"
    assert "missing or unset" in trace["fallback_reason"].lower()
