import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.agent.router import route_query_intent

def test_route_query_intents():
    intent, conf, _ = route_query_intent("What requires my attention right now?")
    assert intent == "founder_attention"

    intent2, conf2, _ = route_query_intent("How much revenue is at risk?")
    assert intent2 == "revenue_at_risk"

    intent3, conf3, _ = route_query_intent("Which deals are stale?")
    assert intent3 == "stale_deals"

    intent4, conf4, _ = route_query_intent("What is our win rate?")
    assert intent4 == "pipeline_health"

    intent5, conf5, _ = route_query_intent("Custom unusual query about drones")
    assert intent5 == "custom_supported_analysis"
