import re
from typing import Dict, Any, Tuple
from skylark_signal.agent.prompts import sanitize_query

INTENT_PATTERNS = [
    ("founder_attention", r"(attention|urgent|priority|top risk|focus|what requires|need to know)"),
    ("revenue_at_risk", r"(revenue at risk|at risk|stalled revenue|jeopardy|risk exposure)"),
    ("stale_deals", r"(stale|stalled|no close date|missing date|tentative date)"),
    ("cross_board_gap", r"(not started|execution gap|sales vs delivery|won deals without|delivery gap)"),
    ("sector_performance", r"(sector|industry|sector breakdown|weighted pipeline by sector)"),
    ("pipeline_health", r"(pipeline|funnel|open pipeline|weighted pipeline|win rate|deals health)"),
    ("operational_health", r"(work order|execution|blocked|overdue|delayed|delivery status)"),
    ("leadership_brief", r"(leadership|meeting|executive summary|brief|pulse)"),
    ("data_quality", r"(data trust|data quality|cleanliness|trust score|accuracy)")
]

def route_query_intent(query: str) -> Tuple[str, float, str]:
    """
    Deterministically maps a user text query to a structured intent.
    Returns (intent_name, confidence_score, matching_rule)
    """
    cleaned_query = sanitize_query(query)
    if not cleaned_query:
        return "founder_attention", 1.0, "default_fallback"

    for intent, pattern in INTENT_PATTERNS:
        if re.search(pattern, cleaned_query, re.IGNORECASE):
            return intent, 0.95, f"regex_pattern_match:{intent}"

    return "custom_supported_analysis", 0.70, "generic_fallback"
