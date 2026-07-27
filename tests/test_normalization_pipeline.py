import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
import pandas as pd
from scripts.normalize_data import run_pipeline
from skylark_signal.data.identifiers import get_file_sha256

def test_full_normalization_pipeline():
    deals_raw_path = "data/raw/deals.xlsx"
    wo_raw_path = "data/raw/work_orders.xlsx"

    deals_sha_before = get_file_sha256(deals_raw_path)
    wo_sha_before = get_file_sha256(wo_raw_path)

    metrics, exported_files = run_pipeline()

    # 1. Check raw file preservation
    deals_sha_after = get_file_sha256(deals_raw_path)
    wo_sha_after = get_file_sha256(wo_raw_path)

    assert deals_sha_before == deals_sha_after, "deals.xlsx raw file modified!"
    assert wo_sha_before == wo_sha_after, "work_orders.xlsx raw file modified!"

    # 2. Check output counts
    assert metrics["row_count_reconciliation"]["deals"]["canonical_output_rows"] == 332
    assert metrics["row_count_reconciliation"]["work_orders"]["canonical_output_rows"] == 176

    # 3. Check Work Order ID uniqueness
    assert metrics["work_order_id_uniqueness"]["is_unique"] is True

    # 4. Check Customer Code Coverage
    assert metrics["customer_code_coverage"]["work_orders_with_deals_customer_match"] == 175

    # 5. Check CSV exports open successfully
    deals_csv = pd.read_csv(exported_files["deals_clean_csv"])
    wo_csv = pd.read_csv(exported_files["work_orders_clean_csv"])

    assert len(deals_csv) == 332
    assert len(wo_csv) == 176
    assert "Import Deal ID" in deals_csv.columns
    assert "Work Order ID" in wo_csv.columns
    # Ensure no fake Deal Reference was created
    assert "Deal Reference (Unavailable)" in wo_csv.columns
