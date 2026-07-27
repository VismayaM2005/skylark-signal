from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
from skylark_signal.config import config
from skylark_signal.analytics.evidence import EvidenceCollector

def is_active_wo(w: Any) -> bool:
    """Checks if a Work Order is active/ongoing."""
    status = (getattr(w, "execution_status", "") or "").lower()
    return status in ("ongoing", "not started", "pending", "executed until current month", "blocked", "delayed", "on hold")

def is_completed_wo(w: Any) -> bool:
    """Checks if a Work Order is completed."""
    status = (getattr(w, "execution_status", "") or "").lower()
    return status in ("completed", "executed", "closed")

def build_operations_metrics(
    work_orders: List[Any],
    evidence_collector: Optional[EvidenceCollector] = None
) -> Dict[str, Any]:
    """
    Computes deterministic operations and delivery metrics from canonical Work Order records.
    """
    total_wo = len(work_orders)
    active_wo_list = [w for w in work_orders if is_active_wo(w)]
    completed_wo_list = [w for w in work_orders if is_completed_wo(w)]

    delayed_wo_list = [w for w in work_orders if (getattr(w, "execution_status", "") or "").lower() in ("delayed", "on hold")]
    blocked_wo_list = [w for w in work_orders if (getattr(w, "execution_status", "") or "").lower() == "blocked"]

    ref_date_str = config.reference_date_iso or "2026-07-27"
    try:
        ref_dt = datetime.strptime(ref_date_str, "%Y-%m-%d")
    except Exception:
        ref_dt = datetime.now()

    overdue_wo_list = []
    for w in active_wo_list:
        due_str = getattr(w, "due_date", None) or getattr(w, "completion_date", None)
        if due_str:
            try:
                due_dt = datetime.strptime(str(due_str), "%Y-%m-%d")
                if due_dt < ref_dt:
                    overdue_wo_list.append(w)
            except Exception:
                pass

    missing_due_date_list = [w for w in work_orders if not w.due_date]
    missing_completion_date_list = [w for w in work_orders if not w.completion_date]

    # Breakdown Distributions
    wo_by_sector: Dict[str, int] = {}
    for w in work_orders:
        sec = getattr(w, "sector", None) or "Unmapped Sector"
        wo_by_sector[sec] = wo_by_sector.get(sec, 0) + 1

    wo_by_status: Dict[str, int] = {}
    for w in work_orders:
        st = getattr(w, "execution_status", None) or "Unmapped Status"
        wo_by_status[st] = wo_by_status.get(st, 0) + 1

    # Financial Project Values
    excl_values = [w.project_value_excl_tax for w in work_orders if w.project_value_excl_tax is not None]
    average_project_value = float(np.mean(excl_values)) if excl_values else 0.0
    median_project_value = float(np.median(excl_values)) if excl_values else 0.0

    # On-Time Completion Rate
    on_time_count = 0
    eval_on_time_count = 0
    for w in completed_wo_list:
        if w.due_date and w.completion_date:
            eval_on_time_count += 1
            try:
                d_dt = datetime.strptime(str(w.due_date), "%Y-%m-%d")
                c_dt = datetime.strptime(str(w.completion_date), "%Y-%m-%d")
                if c_dt <= d_dt:
                    on_time_count += 1
            except Exception:
                pass

    on_time_rate = round(on_time_count / eval_on_time_count, 4) if eval_on_time_count > 0 else 1.0

    # Operations Quality Score (0-100)
    due_date_comp = ((total_wo - len(missing_due_date_list)) / total_wo * 100.0) if total_wo > 0 else 100.0
    status_comp = sum(1 for w in work_orders if w.execution_status != "Unmapped Status") / total_wo * 100.0 if total_wo > 0 else 100.0
    val_comp = len(excl_values) / total_wo * 100.0 if total_wo > 0 else 100.0

    operations_quality_score = round((due_date_comp * 0.40) + (status_comp * 0.30) + (val_comp * 0.30), 1)

    if evidence_collector:
        for w in work_orders:
            evidence_collector.add_evidence(
                metric_name="active_work_orders",
                board_name=getattr(w, "source_sheet", "Work Orders"),
                source_item_id=getattr(w, "source_row_number", 0),
                source_record_id=getattr(w, "source_record_id", "UNK"),
                field_name="execution_status",
                raw_value=str(w.execution_status),
                normalized_value=w.execution_status,
                included_in_calculation=is_active_wo(w),
                inclusion_reason="Active work order" if is_active_wo(w) else "Completed/Closed work order"
            )

    return {
        "total_work_orders": total_wo,
        "active_work_orders": len(active_wo_list),
        "completed_work_orders": len(completed_wo_list),
        "delayed_work_orders": len(delayed_wo_list),
        "blocked_work_orders": len(blocked_wo_list),
        "overdue_work_orders": len(overdue_wo_list),
        "work_orders_missing_due_date": len(missing_due_date_list),
        "work_orders_missing_completion_date": len(missing_completion_date_list),
        "work_orders_by_sector": wo_by_sector,
        "work_orders_by_status": wo_by_status,
        "average_project_value": round(average_project_value, 2),
        "median_project_value": round(median_project_value, 2),
        "on_time_completion_rate": on_time_rate,
        "operations_quality_score": operations_quality_score
    }
