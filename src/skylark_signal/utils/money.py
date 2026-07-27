import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, Any

def parse_money(val: Any) -> Tuple[Optional[float], bool, Any, Optional[str]]:
    """
    Parses currency / monetary strings or numeric values into floats.
    Handles INR, $, commas, spaces, parentheses for negative values e.g. '(100.0)' -> -100.0.
    Returns (parsed_value, success, original_value, warning_reason)
    """
    if val is None:
        return None, True, None, None
    
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ('nan', 'none', 'null', ''):
        return None, True, val, None
    
    # Check for negative numbers in parentheses e.g. (123.45) -> -123.45
    is_negative = False
    if val_str.startswith('(') and val_str.endswith(')'):
        is_negative = True
        val_str = val_str[1:-1].strip()
    elif '-' in val_str:
        is_negative = True
        val_str = val_str.replace('-', '').strip()
        
    # Remove currency symbols, commas, spaces
    cleaned = re.sub(r'[₹$RsINRinr,]', '', val_str).strip()
    
    # Check for text mixed with numbers or non-numeric strings
    try:
        dec = Decimal(cleaned)
        if is_negative:
            dec = -dec
        return float(dec), True, val, None
    except (InvalidOperation, ValueError):
        # Attempt extracting first float / number pattern
        match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
        if match:
            extracted = float(match.group(0))
            if is_negative:
                extracted = -extracted
            return extracted, False, val, f"Extracted number {extracted} from unparsed text string '{val}'"
        return None, False, val, f"Unparseable monetary value '{val}'"

def calculate_implied_tax_rate(
    excl_tax: Optional[float],
    incl_tax: Optional[float]
) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Calculates implied tax rate: (incl_tax - excl_tax) / excl_tax
    Returns (implied_tax_rate, severity, warning_msg)
    """
    if excl_tax is None or incl_tax is None:
        return None, None, None
    
    if excl_tax <= 0:
        return None, "warning", f"Cannot calculate implied tax rate with non-positive exclusive amount {excl_tax}"
    
    rate = (incl_tax - excl_tax) / excl_tax
    
    # Round rate to 4 decimal places for floating point tolerance
    rate = round(rate, 4)
    
    if rate < 0:
        return rate, "error", f"Negative implied tax rate detected: {rate * 100:.2f}% (incl: {incl_tax}, excl: {excl_tax})"
    
    if incl_tax < excl_tax:
        return rate, "error", f"Inclusive tax value ({incl_tax}) is lower than exclusive value ({excl_tax})"
        
    if rate > 0.30:
        return rate, "warning", f"High implied tax rate detected: {rate * 100:.2f}% (exceeds 30%)"
        
    # Standard rates e.g. 18% (0.18), 12% (0.12), 5% (0.05), 0% (0.0)
    # Check if rate deviates significantly from dominant 18% rate
    if round(rate, 2) not in (0.18, 0.12, 0.05, 0.00):
        return rate, "warning", f"Unusual implied tax rate detected: {rate * 100:.2f}% (deviates from standard 18% GST)"
        
    return rate, "info", None
