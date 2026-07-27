import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.agent.context import ConversationContext

def test_conversation_context_turn_tracking():
    context = ConversationContext()
    
    # Turn 1: Specify Energy sector
    context.process_query_turn("How is the Energy pipeline looking?", "pipeline_health")
    assert context.active_sector == "Energy"
    assert context.turns_count == 1

    # Turn 2: Follow-up question without explicit sector
    context.process_query_turn("What about stale deals?", "stale_deals")
    assert context.active_sector == "Energy" # Inherited from Turn 1
    assert context.turns_count == 2

    # Turn 3: Explicit override to Mining
    context.process_query_turn("Switch to Mining pipeline", "pipeline_health")
    assert context.active_sector == "Mining"
    assert context.turns_count == 3

def test_conversation_context_clear():
    context = ConversationContext(active_sector="Solar", turns_count=5)
    context.clear()
    
    assert context.active_sector is None
    assert context.turns_count == 0
    assert len(context.history) == 0
