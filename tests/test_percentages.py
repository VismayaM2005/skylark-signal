import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.utils.percentages import parse_probability

def test_parse_probability_valid():
    prob, ok, _, _ = parse_probability("100%")
    assert prob == 1.0
    assert ok is True

    prob, ok, _, _ = parse_probability("50%")
    assert prob == 0.5
    assert ok is True

    prob, ok, _, _ = parse_probability(0.5)
    assert prob == 0.5
    assert ok is True

    prob, ok, _, _ = parse_probability("50")
    assert prob == 0.5
    assert ok is True

def test_parse_probability_invalid():
    prob, ok, _, warn = parse_probability("150%")
    assert prob is None
    assert ok is False
    assert "outside" in warn or "bounds" in warn

    prob, ok, _, warn = parse_probability("invalid_prob")
    assert prob is None
    assert ok is False

def test_parse_probability_none():
    prob, ok, _, _ = parse_probability(None)
    assert prob is None
    assert ok is True
