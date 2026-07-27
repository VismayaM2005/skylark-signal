import re
from typing import Optional, Tuple, Any

# Standard qualitative mapping for text probability ratings
QUALITATIVE_PROBABILITY_MAP = {
    "high": 0.80,
    "medium": 0.50,
    "med": 0.50,
    "low": 0.20
}

def parse_probability(val: Any) -> Tuple[Optional[float], bool, Any, Optional[str]]:
    """
    Parses probability / percentage inputs into normalized decimal floats between 0.0 and 1.0.
    Rules:
    - Qualitative strings: 'High' -> 0.80, 'Medium' -> 0.50, 'Low' -> 0.20
    - String with '%': divide by 100 e.g. '100%' -> 1.0
    - Numeric value 0 <= val <= 1: treat as decimal probability e.g. 0.5 -> 0.5
    - Numeric value 1 < val <= 100: treat as percentage and divide by 100 e.g. 50 -> 0.5
    - Values outside 0-100: invalid
    - Ambiguous text or empty: None plus warning
    NEVER imputes missing probabilities.
    Returns (parsed_probability, success, original_value, warning_reason)
    """
    if val is None:
        return None, True, None, None
    
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ('nan', 'none', 'null', '', 'closure probability'):
        return None, True, val, None
    
    # Check qualitative rating
    val_lower = val_str.lower()
    if val_lower in QUALITATIVE_PROBABILITY_MAP:
        prob = QUALITATIVE_PROBABILITY_MAP[val_lower]
        return prob, True, val, f"Converted qualitative rating '{val_str}' to decimal probability {prob}"
    
    has_percent = '%' in val_str
    cleaned_str = val_str.replace('%', '').strip()
    
    try:
        num = float(cleaned_str)
    except ValueError:
        return None, False, val, f"Unparseable probability text '{val}'"
        
    if has_percent:
        prob = num / 100.0
    else:
        if 0.0 <= num <= 1.0:
            prob = num
        elif 1.0 < num <= 100.0:
            prob = num / 100.0
        else:
            return None, False, val, f"Probability value {num} is outside valid range (0-100)"
            
    # Bound check
    if 0.0 <= prob <= 1.0:
        return round(prob, 4), True, val, None
    else:
        return None, False, val, f"Calculated probability {prob} is out of bounds [0.0, 1.0]"
