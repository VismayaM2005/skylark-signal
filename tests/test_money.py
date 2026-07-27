import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.utils.money import parse_money, calculate_implied_tax_rate

def test_parse_money_clean():
    val, ok, orig, warn = parse_money("1,234.56")
    assert val == 1234.56
    assert ok is True

    val, ok, orig, warn = parse_money("₹ 500,000")
    assert val == 500000.0
    assert ok is True

    val, ok, orig, warn = parse_money("$12.50")
    assert val == 12.50
    assert ok is True

def test_parse_money_negative_parentheses():
    val, ok, orig, warn = parse_money("(100.0)")
    assert val == -100.0
    assert ok is True

    val_dash, ok, orig, warn = parse_money("-250.0")
    assert val_dash == -250.0
    assert ok is True

def test_parse_money_empty_and_text():
    val, ok, orig, warn = parse_money(None)
    assert val is None
    assert ok is True

    val, ok, orig, warn = parse_money("Approx 5000 INR")
    assert val == 5000.0
    assert ok is False
    assert "Extracted number" in warn

def test_calculate_implied_tax_rate():
    # Standard 18% GST (100 excl, 118 incl)
    rate, sev, msg = calculate_implied_tax_rate(100.0, 118.0)
    assert rate == 0.18
    assert sev == "info"

    # High tax rate > 30%
    rate_high, sev_high, msg_high = calculate_implied_tax_rate(100.0, 150.0)
    assert rate_high == 0.50
    assert sev_high == "warning"
    assert "High implied tax rate" in msg_high

    # Negative rate / incl < excl
    rate_neg, sev_neg, msg_neg = calculate_implied_tax_rate(100.0, 90.0)
    assert rate_neg == -0.10
    assert sev_neg == "error"
    assert "Negative" in msg_neg or "lower" in msg_neg
