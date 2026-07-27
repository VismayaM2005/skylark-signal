import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from unittest.mock import MagicMock, patch

def test_session_state_initialization():
    mock_state = {}
    with patch("streamlit.session_state", mock_state):
        from skylark_signal.ui.state import init_session_state
        init_session_state()

        assert "deals" in mock_state
        assert "work_orders" in mock_state
        assert "status_info" in mock_state
        assert mock_state["active_tab"] == "Ask"
        assert "llm_provider" in mock_state
        assert "selected_llm_model" in mock_state
        assert "openrouter_models" in mock_state
