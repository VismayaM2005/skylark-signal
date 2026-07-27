import re
from datetime import datetime, date
from typing import Optional, Tuple, Any

# Regular expression for Quarter / Financial Period e.g. Q1 FY25, Q3 FY26, Q4 2025, H1 FY26
QUARTER_PERIOD_REGEX = re.compile(r'^(Q[1-4]|H[1-2])\s*(FY\d{2,4}|\d{4})?$', re.IGNORECASE)

def parse_date(val: Any) -> Tuple[Optional[str], Optional[str], str, bool, Optional[str]]:
    """
    Parses dates from various formats (Excel timestamps, ISO strings, DD/MM/YYYY, Quarter text).
    Returns (parsed_date_iso, parsed_period, status, is_ambiguous, failure_reason)
    - parsed_date_iso: YYYY-MM-DD or None
    - parsed_period: Text period e.g. 'Q3 FY26' or None
    - status: 'parsed_exact', 'parsed_period', 'ambiguous', 'failed', 'null'
    - is_ambiguous: True if date format could be DD/MM vs MM/DD without explicit locale hint
    - failure_reason: Description of parsing issue
    """
    if val is None:
        return None, None, 'null', False, None
    
    # Handle Python datetime/date object directly from openpyxl / pandas
    if isinstance(val, (datetime, date)):
        return val.strftime('%Y-%m-%d'), None, 'parsed_exact', False, None
        
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ('nan', 'none', 'null', '', 'nat'):
        return None, None, 'null', False, None
    
    # Check for Quarter / Financial Period text e.g. Q3 FY26
    match_q = QUARTER_PERIOD_REGEX.match(val_str)
    if match_q:
        period_str = val_str.upper()
        return None, period_str, 'parsed_period', False, f"Stored as period '{period_str}' without exact date"
    
    # Check ISO timestamp e.g. 2025-06-30 00:00:00 or 2025-06-30
    iso_match = re.match(r'^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:\s+\d{2}:\d{2}:\d{2})?$', val_str)
    if iso_match:
        y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        try:
            dt = datetime(y, m, d)
            return dt.strftime('%Y-%m-%d'), None, 'parsed_exact', False, None
        except ValueError as e:
            return None, None, 'failed', False, f"Invalid ISO date components: {val_str} ({e})"
            
    # Check DD/MM/YYYY or MM/DD/YYYY slash/dash formats e.g. 31/05/2025 or 03/04/2025
    slash_match = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$', val_str)
    if slash_match:
        part1, part2, year = int(slash_match.group(1)), int(slash_match.group(2)), int(slash_match.group(3))
        
        # If part1 > 12, it MUST be Day-First e.g. 31/05/2025 -> May 31, 2025
        if part1 > 12 and part2 <= 12:
            try:
                dt = datetime(year, part2, part1)
                return dt.strftime('%Y-%m-%d'), None, 'parsed_exact', False, None
            except ValueError:
                return None, None, 'failed', False, f"Invalid date components: {val_str}"
        # If part2 > 12, it MUST be Month-First e.g. 05/31/2025 -> May 31, 2025
        elif part2 > 12 and part1 <= 12:
            try:
                dt = datetime(year, part1, part2)
                return dt.strftime('%Y-%m-%d'), None, 'parsed_exact', False, None
            except ValueError:
                return None, None, 'failed', False, f"Invalid date components: {val_str}"
        # If both part1 <= 12 and part2 <= 12 and part1 != part2, date is ambiguous e.g. 03/04/2025
        elif part1 <= 12 and part2 <= 12 and part1 != part2:
            # Day-first preference as fallback for Indian dataset context, but set ambiguity flag
            try:
                dt = datetime(year, part2, part1) # DD/MM/YYYY
                return dt.strftime('%Y-%m-%d'), None, 'ambiguous', True, f"Ambiguous date format '{val_str}' (could be DD/MM/YYYY or MM/DD/YYYY)"
            except ValueError:
                return None, None, 'failed', True, f"Ambiguous unparseable date '{val_str}'"
        elif part1 == part2:
            try:
                dt = datetime(year, part1, part2)
                return dt.strftime('%Y-%m-%d'), None, 'parsed_exact', False, None
            except ValueError:
                return None, None, 'failed', False, f"Invalid date: {val_str}"

    # Month name parsing e.g. "May 2025", "31 May 2025"
    for fmt in ('%d %B %Y', '%d %b %Y', '%B %Y', '%b %Y'):
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime('%Y-%m-%d'), None, 'parsed_exact', False, None
        except ValueError:
            pass

    return None, None, 'failed', False, f"Unrecognized date format '{val_str}'"
