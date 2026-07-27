from typing import Optional, Union

def format_currency(val: Optional[Union[int, float]], symbol: str = "₹") -> str:
    """Formats a monetary number into human-readable INR string e.g. ₹5,00,000 or ₹0."""
    if val is None:
        return "N/A"
    
    val_float = float(val)
    if val_float == 0:
        return f"{symbol}0"
        
    abs_val = abs(val_float)
    sign = "-" if val_float < 0 else ""
    
    if abs_val >= 10000000: # 1 Crore
        crores = abs_val / 10000000
        return f"{sign}{symbol}{crores:.2f} Cr"
    elif abs_val >= 100000: # 1 Lakh
        lakhs = abs_val / 100000
        return f"{sign}{symbol}{lakhs:.2f} L"
    else:
        return f"{sign}{symbol}{val_float:,.2f}"

def format_percentage(val: Optional[Union[int, float]], precision: int = 1) -> str:
    """Formats float 0.80 -> 80.0%."""
    if val is None:
        return "N/A"
    pct = float(val) * 100.0 if float(val) <= 1.0 else float(val)
    return f"{pct:.{precision}f}%"

def format_number(val: Optional[Union[int, float]]) -> str:
    """Formats numeric value with commas."""
    if val is None:
        return "N/A"
    if isinstance(val, float) and val.is_integer():
        return f"{int(val):,}"
    elif isinstance(val, int):
        return f"{val:,}"
    return f"{float(val):,.2f}"
