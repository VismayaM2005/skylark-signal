import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.agent.planner import QueryPlanner
from skylark_signal.agent.context import ConversationContext

def test_clarification_triggered_for_ambiguous_sector_query():
    planner = QueryPlanner()
    
    # Ambiguous sector query (missing sector dimension)
    is_amb, prompt, dim = planner.check_ambiguity("How is the sector pipeline looking?")
    assert is_amb is True
    assert "sector" in dim
    assert "Which specific sector" in prompt

def test_clarification_not_triggered_for_unambiguous_query():
    planner = QueryPlanner()
    
    # Unambiguous query specifying sector
    is_amb, prompt, dim = planner.check_ambiguity("How is the Mining pipeline looking?")
    assert is_amb is False
    assert prompt is None

def test_clarification_inherited_from_context():
    planner = QueryPlanner()
    context = ConversationContext(active_sector="Mining")
    
    # Query mentions "sector pipeline" but active_sector is already set to Mining in context
    is_amb, prompt, dim = planner.check_ambiguity("How is the sector pipeline looking?", context=context)
    assert is_amb is False # No clarification needed because context has Mining
