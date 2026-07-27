import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from unittest.mock import patch, MagicMock
from skylark_signal.llm.openrouter import fetch_openrouter_models, FALLBACK_MODELS
from skylark_signal.llm.client import LLMClient

def test_fetch_openrouter_models_fallback():
    # Unset key / connection failure should return fallback models
    models = fetch_openrouter_models(api_key=None, force_refresh=True)
    assert len(models) >= 5
    model_ids = [m.id for m in models]
    assert "openai/gpt-4o-mini" in model_ids

@patch("requests.get")
def test_fetch_openrouter_models_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": [
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet"},
            {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B"}
        ]
    }
    mock_get.return_value = mock_resp

    models = fetch_openrouter_models(api_key="test_key", force_refresh=True)
    assert len(models) == 2
    assert models[0].id == "anthropic/claude-3.5-sonnet"

def test_llm_client_deterministic_mode():
    client = LLMClient()
    result = client.generate_text("Test prompt", provider="deterministic")
    assert result is None

@patch("requests.post")
def test_llm_client_openrouter_payload(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Polished response text."}}]
    }
    mock_post.return_value = mock_resp

    client = LLMClient(openrouter_key="sk-or-v1-testkey")
    result = client.generate_text(
        prompt="Pipeline prompt",
        system_prompt="Safety system prompt",
        provider="openrouter",
        model_slug="anthropic/claude-3.5-sonnet"
    )

    assert result == "Polished response text."
    assert mock_post.call_count == 1
    
    # Inspect payload
    _, kwargs = mock_post.call_args
    json_payload = kwargs["json"]
    headers = kwargs["headers"]

    assert json_payload["model"] == "anthropic/claude-3.5-sonnet"
    assert headers["Authorization"] == "Bearer sk-or-v1-testkey"
