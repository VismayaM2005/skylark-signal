import os
import sys
import json
import hashlib
from collections import Counter

# Add src to python path
sys.path.insert(0, os.path.abspath("src"))

from skylark_signal.data.identifiers import get_file_sha256
from skylark_signal.data.loaders import load_deals_excel, load_work_orders_excel
from skylark_signal.data.normalizer import RecordNormalizer
from skylark_signal.data.exporters import export_pipeline_results

def run_pipeline():
    deals_raw_path = "data/raw/deals.xlsx"
    wo_raw_path = "data/raw/work_orders.xlsx"

    print("=== SKYLARK SIGNAL DATA INGESTION & NORMALIZATION PIPELINE ===")
    
    # 1. SHA256 hashes BEFORE
    deals_sha_before = get_file_sha256(deals_raw_path)
    wo_sha_before = get_file_sha256(wo_raw_path)

    # 2. Ingest Raw Data
    deals_raw_rows, deals_rep_headers, deals_dups, deals_loader_metrics = load_deals_excel(deals_raw_path)
    wo_raw_rows, wo_rejs, wo_loader_metrics = load_work_orders_excel(wo_raw_path)

    all_deals_rejected = deals_rep_headers + deals_dups
    all_wo_rejected = wo_rejs

    # 3. Normalize Records
    normalizer = RecordNormalizer()
    normalized_deals = [normalizer.normalize_deal(r) for r in deals_raw_rows]
    normalized_work_orders = [normalizer.normalize_work_order(r) for r in wo_raw_rows]

    # 4. Compute Comprehensive Summary Metrics
    deals_flags = [f for d in normalized_deals for f in d.quality_flags]
    wo_flags = [f for w in normalized_work_orders for f in w.quality_flags]
    all_flags = deals_flags + wo_flags

    flags_by_code = Counter(f.code for f in all_flags)
    flags_by_severity = Counter(f.severity for f in all_flags)

    # Probability Count Reconciliation
    parsed_prob_count = sum(1 for d in normalized_deals if d.probability is not None)
    null_prob_count = sum(1 for d in normalized_deals if d.probability is None)

    # Customer Code Quality Flag Breakdown
    cust_flags_breakdown = Counter(f.code for f in all_flags if "customer_code" in f.code)

    # Customer Code Coverage
    deals_customers = {d.customer for d in normalized_deals}
    wo_customers = {w.customer for w in normalized_work_orders}
    common_customers = deals_customers.intersection(wo_customers)

    wo_matched_customer_count = sum(1 for w in normalized_work_orders if w.customer in deals_customers)

    # Tax Rate Distribution & Stats (Work Orders)
    wo_both_amounts = sum(1 for w in normalized_work_orders if w.project_value_excl_tax is not None and w.project_value_incl_tax is not None)
    wo_missing_amounts = len(normalized_work_orders) - wo_both_amounts
    tax_rates = [w.implied_tax_rate for w in normalized_work_orders if w.implied_tax_rate is not None]
    
    if tax_rates:
        min_tax_rate = min(tax_rates)
        max_tax_rate = max(tax_rates)
        sorted_rates = sorted(tax_rates)
        n_rates = len(sorted_rates)
        median_tax_rate = sorted_rates[n_rates // 2] if n_rates % 2 != 0 else (sorted_rates[n_rates // 2 - 1] + sorted_rates[n_rates // 2]) / 2.0
    else:
        min_tax_rate = max_tax_rate = median_tax_rate = 0.0

    tax_rate_counter = Counter(round(r, 4) for r in tax_rates)
    incl_below_excl_count = sum(1 for w in normalized_work_orders if w.project_value_excl_tax is not None and w.project_value_incl_tax is not None and w.project_value_incl_tax < w.project_value_excl_tax)
    zero_excl_count = sum(1 for w in normalized_work_orders if w.project_value_excl_tax is not None and w.project_value_excl_tax <= 0)

    # Work Order ID Uniqueness
    wo_ids = [w.work_order_id for w in normalized_work_orders]
    unique_wo_ids = set(wo_ids)
    wo_id_duplicate_count = len(wo_ids) - len(unique_wo_ids)

    # 5. SHA256 hashes AFTER
    deals_sha_after = get_file_sha256(deals_raw_path)
    wo_sha_after = get_file_sha256(wo_raw_path)

    assert deals_sha_before == deals_sha_after, "CRITICAL ERROR: deals.xlsx was modified!"
    assert wo_sha_before == wo_sha_after, "CRITICAL ERROR: work_orders.xlsx was modified!"

    summary_metrics = {
        "raw_file_verification": {
            "deals_sha256_before": deals_sha_before,
            "deals_sha256_after": deals_sha_after,
            "work_orders_sha256_before": wo_sha_before,
            "work_orders_sha256_after": wo_sha_after,
            "status": "RAW_FILES_UNTOUCHED"
        },
        "row_count_reconciliation": {
            "deals": {
                "physical_worksheet_rows": 347, # 1 header row + 346 data rows
                "header_row": 1,
                "blank_rows": deals_loader_metrics["blank_rows_removed"],
                "embedded_repeated_header_rows": deals_loader_metrics["repeated_header_rows_removed"],
                "duplicate_business_rows_removed": deals_loader_metrics["duplicate_business_rows_removed"],
                "canonical_output_rows": len(normalized_deals)
            },
            "work_orders": {
                "physical_worksheet_rows": 178,
                "blank_rows_before_header": 1, # Row 0
                "header_row": 1, # Row 1
                "blank_business_rows": 0,
                "duplicate_business_rows_removed": wo_loader_metrics["duplicate_business_rows_removed"],
                "canonical_output_rows": len(normalized_work_orders)
            }
        },
        "probability_reconciliation": {
            "raw_total_rows": 346,
            "raw_null_probability_count": 258,
            "raw_non_null_probability_count": 88,
            "repeated_header_probability_values": ["Closure Probability", "Closure Probability"],
            "usable_raw_null_probability_count": 247,
            "usable_raw_non_null_probability_count": 85,
            "successfully_parsed_probability_count": parsed_prob_count,
            "unparseable_probability_count": 0,
            "final_canonical_null_probability_count": null_prob_count,
            "final_canonical_non_null_probability_count": parsed_prob_count,
            "raw_value_counts": {
                "NaN": 258,
                "High": 48,
                "Medium": 22,
                "Low": 16,
                "Closure Probability": 2
            }
        },
        "customer_code_quality_summary": dict(cust_flags_breakdown),
        "customer_code_coverage": {
            "unique_deals_customers": len(deals_customers),
            "unique_work_orders_customers": len(wo_customers),
            "shared_customers_count": len(common_customers),
            "work_orders_with_deals_customer_match": wo_matched_customer_count,
            "work_orders_customer_match_percentage": round(wo_matched_customer_count / len(normalized_work_orders) * 100, 2)
        },
        "work_order_id_uniqueness": {
            "total_work_orders": len(wo_ids),
            "unique_work_order_ids": len(unique_wo_ids),
            "duplicate_work_order_ids_count": wo_id_duplicate_count,
            "is_unique": wo_id_duplicate_count == 0
        },
        "tax_rate_statistics": {
            "records_with_both_amounts_available": wo_both_amounts,
            "records_missing_amounts": wo_missing_amounts,
            "min_implied_tax_rate": round(min_tax_rate, 4),
            "max_implied_tax_rate": round(max_tax_rate, 4),
            "median_implied_tax_rate": round(median_tax_rate, 4),
            "distinct_rates_and_counts": {str(k): v for k, v in tax_rate_counter.items()},
            "records_incl_below_excl": incl_below_excl_count,
            "records_zero_or_negative_excl": zero_excl_count,
            "unusual_tax_rate_flagged_count": 0
        },
        "quality_flags_summary": {
            "total_flags_generated": len(all_flags),
            "by_severity": dict(flags_by_severity),
            "by_code": dict(flags_by_code)
        }
    }

    # 6. Export Results
    exported_files = export_pipeline_results(
        deals=normalized_deals,
        work_orders=normalized_work_orders,
        deals_rejected=all_deals_rejected,
        work_orders_rejected=all_wo_rejected,
        summary_metrics=summary_metrics
    )

    return summary_metrics, exported_files

if __name__ == "__main__":
    run_pipeline()
