import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
import pandas as pd
from skylark_signal.utils.text import clean_text, normalize_customer_code, map_category
from skylark_signal.utils.money import parse_money, calculate_implied_tax_rate
from skylark_signal.utils.percentages import parse_probability
from skylark_signal.utils.dates import parse_date
from skylark_signal.data.identifiers import (
    generate_source_record_id,
    generate_synthetic_deal_id,
    validate_work_order_id,
    get_file_sha256
)
from skylark_signal.data.normalizer import RecordNormalizer
from scripts.normalize_data import run_pipeline

def test_qa_customer_code_normal():
    code, flag, sev, warn = normalize_customer_code("COMPANY005")
    assert code == "COMPANY_005"
    assert flag == "customer_code_normalized"
    assert sev == "info"

def test_qa_truly_malformed_customer_code():
    code, flag, sev, warn = normalize_customer_code("INVALID_CLIENT_X")
    assert flag == "malformed_customer_code"
    assert sev == "warning"

def test_qa_missing_customer_code():
    code, flag, sev, warn = normalize_customer_code(None)
    assert code is None
    assert flag == "missing_customer_code"
    assert sev == "error"

def test_qa_currency_symbols():
    val1, ok1, _, _ = parse_money("₹ 500,000")
    assert val1 == 500000.0
    val2, ok2, _, _ = parse_money("$1,250.50")
    assert val2 == 1250.50

def test_qa_comma_formatted_money():
    val, ok, _, _ = parse_money("1,000,000.00")
    assert val == 1000000.0
    assert ok is True

def test_qa_parenthesized_negative_values():
    val, ok, _, _ = parse_money("(500.0)")
    assert val == -500.0
    assert ok is True

def test_qa_invalid_money():
    val, ok, _, warn = parse_money("NOT_A_MONEY_STRING")
    assert val is None
    assert ok is False

def test_qa_percentage_strings():
    prob, ok, _, _ = parse_probability("100%")
    assert prob == 1.0
    prob2, ok2, _, _ = parse_probability("50%")
    assert prob2 == 0.5

def test_qa_decimal_probabilities():
    prob, ok, _, _ = parse_probability(0.5)
    assert prob == 0.5
    assert ok is True

def test_qa_whole_number_percentages():
    prob, ok, _, _ = parse_probability(50)
    assert prob == 0.5
    assert ok is True

def test_qa_invalid_probabilities():
    prob1, ok1, _, _ = parse_probability("150%")
    assert prob1 is None
    assert ok1 is False

    prob2, ok2, _, _ = parse_probability("-10%")
    assert prob2 is None
    assert ok2 is False

def test_qa_iso_dates():
    dt_str, period, status, amb, _ = parse_date("2025-06-30 00:00:00")
    assert dt_str == "2025-06-30"
    assert status == "parsed_exact"

def test_qa_day_first_dates():
    dt_str, period, status, amb, _ = parse_date("31/05/2025")
    assert dt_str == "2025-05-31"
    assert status == "parsed_exact"

def test_qa_ambiguous_dates():
    dt_str, period, status, amb, _ = parse_date("03/04/2025")
    assert amb is True
    assert status == "ambiguous"

def test_qa_financial_quarter_text():
    dt_str, period, status, amb, _ = parse_date("Q3 FY26")
    assert dt_str is None
    assert period == "Q3 FY26"
    assert status == "parsed_period"

def test_qa_synthetic_deal_id_determinism():
    id1 = generate_synthetic_deal_id("HASH123", 5, "Sakura", "COMPANY_002")
    id2 = generate_synthetic_deal_id("HASH123", 5, "Sakura", "COMPANY_002")
    assert id1 == id2
    assert id1.startswith("IMPORT-DEAL-")

def test_qa_synthetic_deal_id_uniqueness():
    id1 = generate_synthetic_deal_id("HASH123", 5, "Sakura", "COMPANY_002")
    id2 = generate_synthetic_deal_id("HASH123", 6, "Sakura", "COMPANY_002")
    assert id1 != id2

def test_qa_missing_work_order_id():
    valid, warn = validate_work_order_id(None)
    assert valid is False
    assert "Missing" in warn

def test_qa_unknown_categories():
    normalizer = RecordNormalizer()
    raw_deal = {
        "source_file": "deals.xlsx",
        "source_sheet": "Deal tracker",
        "source_row_number": 2,
        "file_hash": "HASH",
        "raw_values": {
            "Deal Name": "Test",
            "Client Code": "COMPANY001",
            "Sector/service": "Quantum Sector",
            "Deal Stage": "Z. Ultra Stage",
            "Deal Status": "Hyper Status"
        }
    }
    rec = normalizer.normalize_deal(raw_deal)
    codes = [f.code for f in rec.quality_flags]
    assert "unknown_sector" in codes
    assert "unknown_stage" in codes
    assert "unknown_status" in codes

def test_qa_implied_tax_rate_calculation():
    rate, sev, msg = calculate_implied_tax_rate(100.0, 118.0)
    assert rate == 0.18

def test_qa_inclusive_value_below_exclusive():
    rate, sev, msg = calculate_implied_tax_rate(100.0, 90.0)
    assert sev == "error"
    assert "lower" in msg or "Negative" in msg

def test_qa_zero_exclusive_value():
    rate, sev, msg = calculate_implied_tax_rate(0.0, 100.0)
    assert rate is None
    assert sev == "warning"
    assert "non-positive" in msg

def test_qa_no_fabricated_deal_reference():
    normalizer = RecordNormalizer()
    raw_wo = {
        "source_file": "work_orders.xlsx",
        "source_sheet": "work order tracker",
        "source_row_number": 2,
        "file_hash": "HASH",
        "raw_values": {
            "Deal name masked": "Scooby-Doo",
            "Customer Name Code": "WOCOMPANY_002",
            "Serial #": "SDPLDEAL-075"
        }
    }
    rec = normalizer.normalize_work_order(raw_wo)
    assert rec.deal_reference is None

def test_qa_no_probability_imputation():
    normalizer = RecordNormalizer()
    raw_deal = {
        "source_file": "deals.xlsx",
        "source_sheet": "Deal tracker",
        "source_row_number": 2,
        "file_hash": "HASH",
        "raw_values": {
            "Deal Name": "Test",
            "Client Code": "COMPANY001",
            "Closure Probability": None
        }
    }
    rec = normalizer.normalize_deal(raw_deal)
    assert rec.probability is None

def test_qa_pipeline_repeatability_and_hash_preservation():
    deals_raw_path = "data/raw/deals.xlsx"
    wo_raw_path = "data/raw/work_orders.xlsx"

    h1_before = get_file_sha256(deals_raw_path)
    h2_before = get_file_sha256(wo_raw_path)

    m1, e1 = run_pipeline()
    
    h1_after = get_file_sha256(deals_raw_path)
    h2_after = get_file_sha256(wo_raw_path)

    assert h1_before == h1_after
    assert h2_before == h2_after

    # Run pass 2
    m2, e2 = run_pipeline()

    # Compare hashes of exported clean CSVs
    csv_deals_pass1 = get_file_sha256(e1["deals_clean_csv"])
    csv_deals_pass2 = get_file_sha256(e2["deals_clean_csv"])
    assert csv_deals_pass1 == csv_deals_pass2, "deals_clean.csv is not repeatable!"

    csv_wo_pass1 = get_file_sha256(e1["work_orders_clean_csv"])
    csv_wo_pass2 = get_file_sha256(e2["work_orders_clean_csv"])
    assert csv_wo_pass1 == csv_wo_pass2, "work_orders_clean.csv is not repeatable!"
