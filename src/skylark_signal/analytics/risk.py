from typing import List, Dict, Any, Optional
import numpy as np
from skylark_signal.analytics.evidence import EvidenceCollector
from skylark_signal.analytics.pipeline_metrics import is_open_deal
from skylark_signal.analytics.operations_metrics import is_active_wo
from datetime import datetime
from skylark_signal.config import config

def build_revenue_at_risk(
    deals: List[Any],
    work_orders: List[Any],
    evidence_collector: Optional[EvidenceCollector] = None
) -> Dict[str, Any]:
    """
    Computes a transparent, rule-based, non-overlapping Revenue at Risk model.
    Guarantees 0 double-counting across risk buckets.
    """
    ref_date_str = config.reference_date_iso or "2026-07-27"
    try:
        ref_dt = datetime.strptime(ref_date_str, "%Y-%m-%d")
    except Exception:
        ref_dt = datetime.now()

    risk_items: List[Dict[str, Any]] = []
    seen_wo_ids = set()
    seen_deal_ids = set()

    # Bucket 1: Blocked or Delayed Active Work Orders
    blocked_delayed_wo = [
        w for w in work_orders
        if is_active_wo(w) and (getattr(w, "execution_status", "") or "").lower() in ("blocked", "delayed", "on hold")
    ]
    
    b_d_val = float(sum(w.project_value_excl_tax or 0.0 for w in blocked_delayed_wo))
    b_d_rec_ids = [str(getattr(w, "source_record_id", w.work_order_id)) for w in blocked_delayed_wo]
    for w in blocked_delayed_wo:
        seen_wo_ids.add(w.work_order_id)

    if blocked_delayed_wo:
        risk_items.append({
            "risk_id": "RISK-001",
            "category": "blocked_or_delayed_active_work_orders",
            "title": "Blocked or Delayed Work Orders Contract Value",
            "value_at_risk": round(b_d_val, 2),
            "source_board": "Work Orders",
            "source_record_ids": b_d_rec_ids,
            "formula": "Sum(project_value_excl_tax) for active work orders with status Blocked/Delayed/On Hold",
            "confidence_level": 0.95,
            "caveat": "Based on self-reported execution status on Work Orders board."
        })

    # Bucket 2: Overdue Active Work Orders (excluding Bucket 1)
    overdue_wo = []
    for w in work_orders:
        if is_active_wo(w) and w.work_order_id not in seen_wo_ids:
            due_str = getattr(w, "due_date", None) or getattr(w, "completion_date", None)
            if due_str:
                try:
                    due_dt = datetime.strptime(str(due_str), "%Y-%m-%d")
                    if due_dt < ref_dt:
                        overdue_wo.append(w)
                        seen_wo_ids.add(w.work_order_id)
                except Exception:
                    pass

    overdue_val = float(sum(w.project_value_excl_tax or 0.0 for w in overdue_wo))
    overdue_rec_ids = [str(getattr(w, "source_record_id", w.work_order_id)) for w in overdue_wo]

    if overdue_wo:
        risk_items.append({
            "risk_id": "RISK-002",
            "category": "overdue_active_work_orders",
            "title": "Overdue Active Work Orders Contract Value",
            "value_at_risk": round(overdue_val, 2),
            "source_board": "Work Orders",
            "source_record_ids": overdue_rec_ids,
            "formula": "Sum(project_value_excl_tax) for active work orders past due_date (excluding blocked/delayed)",
            "confidence_level": 0.90,
            "caveat": "Assumes target completion date has passed without logged completion."
        })

    # Bucket 3: Stale Late-Stage Deals
    stale_deals = []
    for d in deals:
        if is_open_deal(d):
            stg = (getattr(d, "stage", "") or "").lower()
            # Late stage: proposal, negotiation, decision maker
            if any(term in stg for term in ("proposal", "negotiation", "decision maker", "shortlisted")):
                is_stale = False
                if d.expected_close_date:
                    try:
                        c_dt = datetime.strptime(str(d.expected_close_date), "%Y-%m-%d")
                        if (ref_dt - c_dt).days > config.stale_deal_days:
                            is_stale = True
                    except Exception:
                        pass
                else:
                    if not d.expected_close_period:
                        is_stale = True
                        
                if is_stale:
                    stale_deals.append(d)
                    seen_deal_ids.add(d.deal_id)

    stale_val = float(sum(d.deal_value or 0.0 for d in stale_deals))
    stale_rec_ids = [str(getattr(d, "source_record_id", d.deal_id)) for d in stale_deals]

    if stale_deals:
        risk_items.append({
            "risk_id": "RISK-003",
            "category": "stale_late_stage_deals",
            "title": "Stale Late-Stage Opportunity Pipeline",
            "value_at_risk": round(stale_val, 2),
            "source_board": "Deals",
            "source_record_ids": stale_rec_ids,
            "formula": "Sum(deal_value) for open late-stage deals past tentative close date or without close date",
            "confidence_level": 0.85,
            "caveat": "Late-stage deals with stalled momentum carry high risk of deal slippage or loss."
        })

    # Bucket 4: High-Value Open Deals Missing Win Probability (excluding Bucket 3)
    open_vals = [d.deal_value for d in deals if is_open_deal(d) and d.deal_value is not None]
    high_val_threshold = float(np.percentile(open_vals, 75)) if open_vals else 500000.0

    missing_prob_deals = [
        d for d in deals
        if is_open_deal(d) and d.deal_id not in seen_deal_ids and (d.deal_value or 0.0) >= high_val_threshold and d.probability is None
    ]
    missing_prob_val = float(sum(d.deal_value or 0.0 for d in missing_prob_deals))
    missing_prob_ids = [str(getattr(d, "source_record_id", d.deal_id)) for d in missing_prob_deals]

    if missing_prob_deals:
        risk_items.append({
            "risk_id": "RISK-004",
            "category": "high_value_missing_probability_deals",
            "title": "High-Value Deals Missing Win Probability",
            "value_at_risk": round(missing_prob_val, 2),
            "source_board": "Deals",
            "source_record_ids": missing_prob_ids,
            "formula": "Sum(deal_value) for open deals >= 75th percentile value missing closure probability",
            "confidence_level": 0.80,
            "caveat": "Lack of probability rating impairs weighted pipeline forecasting accuracy."
        })

    total_revenue_at_risk = float(sum(item["value_at_risk"] for item in risk_items))

    if evidence_collector:
        for item in risk_items:
            for r_id in item["source_record_ids"]:
                evidence_collector.add_evidence(
                    metric_name=f"revenue_at_risk:{item['category']}",
                    board_name=item["source_board"],
                    source_item_id=r_id,
                    source_record_id=r_id,
                    field_name="value_at_risk",
                    raw_value=str(item["value_at_risk"]),
                    normalized_value=item["value_at_risk"],
                    inclusion_reason=item["formula"]
                )

    return {
        "total_revenue_at_risk": round(total_revenue_at_risk, 2),
        "risk_items_count": len(risk_items),
        "risk_breakdown_by_category": {item["category"]: item["value_at_risk"] for item in risk_items},
        "risk_items": risk_items,
        "double_counting_prevented": True
    }
