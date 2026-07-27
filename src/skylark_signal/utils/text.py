import re
import unicodedata
from typing import Optional, Tuple, Dict, Any

def clean_text(val: Any) -> Optional[str]:
    """
    Trim whitespace, collapse internal whitespace, and normalize Unicode.
    Returns None if val is empty or null.
    """
    if val is None:
        return None
    
    val_str = str(val)
    val_str = unicodedata.normalize('NFKC', val_str)
    val_str = val_str.strip()
    if not val_str or val_str.lower() in ('nan', 'none', 'null'):
        return None
    
    val_str = re.sub(r'\s+', ' ', val_str)
    return val_str

def normalize_customer_code(val: Any) -> Tuple[Optional[str], str, str, Optional[str]]:
    """
    Normalize customer codes:
    COMPANY005 -> COMPANY_005
    COMPANY_005 -> COMPANY_005
    WOCOMPANY_005 -> COMPANY_005
    WOCOMPANY_02 -> COMPANY_002
    
    Returns (canonical_code, flag_code, severity, warning_message)
    - flag_code: 'customer_code_normalized', 'customer_code_fallback', 'malformed_customer_code', 'missing_customer_code'
    - severity: 'info', 'warning', 'error'
    """
    cleaned = clean_text(val)
    if not cleaned:
        return None, "missing_customer_code", "error", "Missing customer code"
    
    # Match standard expected format: COMPANY005, COMPANY_005, WOCOMPANY_005, WOCOMPANY005 with 3 digits
    standard_match = re.search(r'^(?:WO)?COMPANY[_\s]*(\d{3})$', cleaned, re.IGNORECASE)
    if standard_match:
        num = int(standard_match.group(1))
        canonical = f"COMPANY_{num:03d}"
        return canonical, "customer_code_normalized", "info", None

    # Match format with non-standard digit padding e.g. WOCOMPANY_02 or COMPANY_5
    digit_match = re.search(r'^(?:WO)?COMPANY[_\s]*(\d+)$', cleaned, re.IGNORECASE)
    if digit_match:
        num = int(digit_match.group(1))
        canonical = f"COMPANY_{num:03d}"
        return canonical, "customer_code_fallback", "info", f"Normalized customer code '{cleaned}' using zero-padding fallback"
        
    # Generic fallback digit extraction if string contains digits
    generic_match = re.search(r'(\d+)', cleaned)
    if generic_match:
        num = int(generic_match.group(1))
        canonical = f"COMPANY_{num:03d}"
        return canonical, "malformed_customer_code", "warning", f"Malformed customer code '{cleaned}' normalized using fallback digit extraction"
    
    return cleaned, "malformed_customer_code", "warning", f"Malformed customer code '{cleaned}' - pattern match failed"

def map_category(val: Any, mapping_dict: Dict[str, Any]) -> Tuple[Optional[str], bool, Optional[str]]:
    """
    Map raw category string to canonical string using a mapping dictionary.
    Returns (canonical_val, is_mapped, rule_name)
    """
    cleaned = clean_text(val)
    if not cleaned:
        return None, True, "empty_value"
    
    if cleaned in mapping_dict:
        target = mapping_dict[cleaned]
        if isinstance(target, dict):
            return target.get("canonical_stage", cleaned), True, "exact_match_dict"
        return str(target), True, "exact_match"
    
    for k, v in mapping_dict.items():
        if k.lower() == cleaned.lower():
            if isinstance(v, dict):
                return v.get("canonical_stage", cleaned), True, "case_insensitive_dict"
            return str(v), True, "case_insensitive"
            
    return cleaned, False, "unmapped_raw_value"
