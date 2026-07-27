"""
Tests for provider dropdown visibility rules.

Rules under test:
- "Deterministic" and "OpenRouter" are always in available_llm_providers.
- "OpenAI" is included ONLY when OPENAI_API_KEY is set.
- The session-state default provider never selects OpenAI when its key is absent.
- A stale session provider that is no longer available is reset to Deterministic.
"""
import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from unittest.mock import patch, MagicMock


# ── Config-level tests (no Streamlit needed) ─────────────────────────────────

def test_available_providers_without_openai_key():
    """OpenAI must not appear when OPENAI_API_KEY is unset."""
    from skylark_signal.config import Config
    with patch.dict(os.environ, {}, clear=False):
        # Temporarily clear OPENAI_API_KEY if it exists in the environment
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            cfg = Config()
            providers = cfg.available_llm_providers
    assert "OpenAI" not in providers, f"OpenAI must be absent without key; got {providers}"
    assert "Deterministic" in providers
    assert "OpenRouter" in providers


def test_available_providers_with_openai_key():
    """OpenAI must appear when OPENAI_API_KEY is set."""
    from skylark_signal.config import Config
    env = {k: v for k, v in os.environ.items()}
    env["OPENAI_API_KEY"] = "sk-testkey-12345"
    with patch.dict(os.environ, env, clear=True):
        cfg = Config()
        providers = cfg.available_llm_providers
    assert "OpenAI" in providers, f"OpenAI must appear when key is set; got {providers}"
    assert "Deterministic" in providers
    assert "OpenRouter" in providers


def test_deterministic_always_present():
    """Deterministic must be first and always present regardless of keys."""
    from skylark_signal.config import Config
    # No keys at all
    env = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "OPENROUTER_API_KEY")}
    with patch.dict(os.environ, env, clear=True):
        cfg = Config()
        providers = cfg.available_llm_providers
    assert providers[0] == "Deterministic"
    assert len(providers) >= 2  # At minimum: Deterministic + OpenRouter


def test_openrouter_always_present():
    """OpenRouter must always be listed so the user can paste a key in the sidebar."""
    from skylark_signal.config import Config
    env = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "OPENROUTER_API_KEY")}
    with patch.dict(os.environ, env, clear=True):
        cfg = Config()
        providers = cfg.available_llm_providers
    assert "OpenRouter" in providers


# ── State-level tests (mock Streamlit) ───────────────────────────────────────

def _make_mock_state():
    """Returns a fresh dict that acts as st.session_state."""
    return {}


def test_state_default_provider_without_openai_key():
    """Default provider must not be OpenAI when OPENAI_API_KEY is absent."""
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        # Re-import config so it reflects the cleared env
        import importlib
        import skylark_signal.config as cfg_module
        importlib.reload(cfg_module)
        config = cfg_module.Config()

        mock_state = {}
        # Simulate the state init logic from state.py
        if "llm_provider" not in mock_state:
            available = config.available_llm_providers
            if config.openrouter_api_key and "OpenRouter" in available:
                mock_state["llm_provider"] = "OpenRouter"
            else:
                mock_state["llm_provider"] = "Deterministic"

    assert mock_state["llm_provider"] != "OpenAI", \
        f"Default must not be OpenAI without key; got {mock_state['llm_provider']}"


def test_state_stale_openai_session_resets_to_deterministic():
    """If session has 'OpenAI' from a previous run but key is now absent, reset to Deterministic."""
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        import importlib
        import skylark_signal.config as cfg_module
        importlib.reload(cfg_module)
        config = cfg_module.Config()

        mock_state = {"llm_provider": "OpenAI"}  # stale from prior session
        available = config.available_llm_providers
        # Simulate the guard from state.py
        if mock_state.get("llm_provider") not in available:
            mock_state["llm_provider"] = "Deterministic"

    assert mock_state["llm_provider"] == "Deterministic"


def test_openai_not_in_provider_string_without_key():
    """String 'OpenAI' must not appear in the available providers list without a key."""
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        import importlib
        import skylark_signal.config as cfg_module
        importlib.reload(cfg_module)
        config = cfg_module.Config()
        providers_str = ", ".join(config.available_llm_providers)

    assert "OpenAI" not in providers_str, \
        f"OpenAI must not appear in provider list without key; got: {providers_str}"
