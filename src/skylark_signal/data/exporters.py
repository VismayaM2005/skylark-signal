import os
import json
import pandas as pd
from typing import List, Dict, Any
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord

def get_highest_severity(flags: List[Any]) -> str:
    """Returns the highest severity string among quality flags."""
    severities = {f.severity for f in flags}
    if "error" in severities:
        return "error"
    if "warning" in severities:
        return "warning"
    if "info" in severities:
        return "info"
    return "clean"

def format_flag_summary(flags: List[Any]) -> str:
    """Formats flags into a pipe-separated string summary."""
    if not flags:
        return ""
    return " | ".join(f"[{f.code}] {f.message}" for f in flags)

def export_pipeline_results(
    deals: List[CanonicalDealRecord],
    work_orders: List[CanonicalWorkOrderRecord],
    deals_rejected: List[Dict[str, Any]],
    work_orders_rejected: List[Dict[str, Any]],
    summary_metrics: Dict[str, Any],
    output_dir: str = "data/processed"
) -> Dict[str, str]:
    """
    Exports clean CSVs, JSON representations, rejected row files,
    data quality issues CSV, and normalization_summary.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    # 1. Deals Clean CSV (monday.com Import Format)
    deals_csv_rows = []
    for d in deals:
        deals_csv_rows.append({
            "Import Deal ID": d.deal_id,
            "Deal Name": d.deal_name,
            "Customer Code": d.customer,
            "Sector": d.sector or "",
            "Deal Stage": d.stage,
            "Deal Status": d.status,
            "Deal Value": d.deal_value if d.deal_value is not None else "",
            "Win Probability": d.probability if d.probability is not None else "",
            "Tentative Close Date": d.expected_close_date or "",
            "Tentative Close Period": d.expected_close_period or "",
            "Actual Close Date": d.actual_close_date or "",
            "Deal Owner": d.owner or "",
            "Created Date": d.created_date or "",
            "Product or Service": d.product_or_service or "",
            "Data Quality Severity": get_highest_severity(d.quality_flags),
            "Data Quality Issues": format_flag_summary(d.quality_flags),
            "Source Row Number": d.source_row_number
        })
    df_deals_csv = pd.DataFrame(deals_csv_rows)
    deals_csv_path = os.path.join(output_dir, "deals_clean.csv")
    df_deals_csv.to_csv(deals_csv_path, index=False)
    generated_files["deals_clean_csv"] = deals_csv_path

    # 2. Work Orders Clean CSV (monday.com Import Format)
    wo_csv_rows = []
    for w in work_orders:
        wo_csv_rows.append({
            "Work Order ID": w.work_order_id,
            "Work Order Name": w.work_order_name,
            "Deal Reference (Unavailable)": "", # Blank per prompt rule
            "Customer Code": w.customer,
            "Sector": w.sector or "",
            "Nature of Work": w.nature_of_work or "",
            "Execution Status": w.execution_status,
            "Contract Value Excl Tax": w.project_value_excl_tax if w.project_value_excl_tax is not None else "",
            "Contract Value Incl Tax": w.project_value_incl_tax if w.project_value_incl_tax is not None else "",
            "Implied Tax Rate": w.implied_tax_rate if w.implied_tax_rate is not None else "",
            "Probable Start Date": w.start_date or "",
            "Probable End Date": w.due_date or "",
            "Completion Date": w.completion_date or "",
            "Invoice Status": w.invoice_status or "",
            "Billing Status": w.billing_status or "",
            "Owner": w.owner or "",
            "Data Quality Severity": get_highest_severity(w.quality_flags),
            "Data Quality Issues": format_flag_summary(w.quality_flags),
            "Source Row Number": w.source_row_number
        })
    df_wo_csv = pd.DataFrame(wo_csv_rows)
    wo_csv_path = os.path.join(output_dir, "work_orders_clean.csv")
    df_wo_csv.to_csv(wo_csv_path, index=False)
    generated_files["work_orders_clean_csv"] = wo_csv_path

    # 3. Deals & Work Orders Clean JSON
    deals_json_path = os.path.join(output_dir, "deals_clean.json")
    with open(deals_json_path, "w") as f:
        json.dump([d.model_dump() for d in deals], f, indent=2)
    generated_files["deals_clean_json"] = deals_json_path

    wo_json_path = os.path.join(output_dir, "work_orders_clean.json")
    with open(wo_json_path, "w") as f:
        json.dump([w.model_dump() for w in work_orders], f, indent=2)
    generated_files["work_orders_clean_json"] = wo_json_path

    # 4. Rejected / Duplicate Row CSVs
    deals_rej_path = os.path.join(output_dir, "deals_rejected_or_duplicate_rows.csv")
    pd.DataFrame(deals_rejected).to_csv(deals_rej_path, index=False)
    generated_files["deals_rejected_csv"] = deals_rej_path

    wo_rej_path = os.path.join(output_dir, "work_orders_rejected_rows.csv")
    pd.DataFrame(work_orders_rejected).to_csv(wo_rej_path, index=False)
    generated_files["work_orders_rejected_csv"] = wo_rej_path

    # 5. Data Quality Issues Log CSV
    all_issues = []
    for d in deals:
        for f in d.quality_flags:
            all_issues.append({
                "dataset": "Deals",
                "record_id": d.deal_id,
                "source_row_number": d.source_row_number,
                "code": f.code,
                "severity": f.severity,
                "field": f.field or "",
                "message": f.message,
                "raw_value": f.raw_value or "",
                "affects_metrics": f.affects_metrics,
                "recommended_action": f.recommended_action or ""
            })
    for w in work_orders:
        for f in w.quality_flags:
            all_issues.append({
                "dataset": "Work Orders",
                "record_id": w.work_order_id,
                "source_row_number": w.source_row_number,
                "code": f.code,
                "severity": f.severity,
                "field": f.field or "",
                "message": f.message,
                "raw_value": f.raw_value or "",
                "affects_metrics": f.affects_metrics,
                "recommended_action": f.recommended_action or ""
            })
    issues_csv_path = os.path.join(output_dir, "data_quality_issues.csv")
    pd.DataFrame(all_issues).to_csv(issues_csv_path, index=False)
    generated_files["data_quality_issues_csv"] = issues_csv_path

    # 6. Normalization Summary JSON
    summary_json_path = os.path.join(output_dir, "normalization_summary.json")
    with open(summary_json_path, "w") as f:
        json.dump(summary_metrics, f, indent=2)
    generated_files["normalization_summary_json"] = summary_json_path

    return generated_files
