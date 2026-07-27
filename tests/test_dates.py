import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from datetime import datetime
from skylark_signal.utils.dates import parse_date

def test_parse_date_iso():
    dt_str, period, status, amb, fail = parse_date("2025-06-30 00:00:00")
    assert dt_str == "2025-06-30"
    assert period is None
    assert status == "parsed_exact"
    assert amb is False

def test_parse_date_day_first():
    dt_str, period, status, amb, fail = parse_date("31/05/2025")
    assert dt_str == "2025-05-31"
    assert status == "parsed_exact"
    assert amb is False

def test_parse_date_ambiguous():
    dt_str, period, status, amb, fail = parse_date("03/04/2025")
    assert dt_str is not None
    assert amb is True
    assert status == "ambiguous"

def test_parse_date_quarter_period():
    dt_str, period, status, amb, fail = parse_date("Q3 FY26")
    assert dt_str is None
    assert period == "Q3 FY26"
    assert status == "parsed_period"
    assert amb is False

def test_parse_date_datetime_obj():
    dt_obj = datetime(2025, 8, 15)
    dt_str, period, status, amb, fail = parse_date(dt_obj)
    assert dt_str == "2025-08-15"
    assert status == "parsed_exact"
