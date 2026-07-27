from typing import List, Dict, Any, Optional
from skylark_signal.analytics.evidence import EvidenceCollector

def calculate_financial_score(amount: float) -> float:
    """Normalizes financial impact amount into a 0-100 score."""
    if amount <= 0:
        return 10.0
    elif amount < 500000: # < 5L
        return 40.0
    elif amount < 2000000: # < 20L
        return 70.0
    elif amount < 5000000: # < 50L
        return 85.0
    else:
        return 100.0

def build_attention_queue(
    deals: List[Any],
    work_orders: List[Any],
    risk_bundle: Dict[str, Any],
    pipeline_metrics: Dict[str, Any],
    ops_metrics: Dict[str, Any],
    cross_board_metrics: Dict[str, Any],
    evidence_collector: Optional[EvidenceCollector] = None
) -> List[Dict[str, Any]]:
    """
    Generates a ranked, scored Founder Attention Queue for leadership.
    """
    raw_queue_items: List[Dict[str, Any]] = []

    # 1. Blocked Work Orders Issue
    blocked_wo_count = ops_metrics.get("blocked_work_orders", 0)
    if blocked_wo_count > 0:
        blocked_wo_records = [w for w in work_orders if (getattr(w, "execution_status", "") or "").lower() == "blocked"]
        blocked_val = sum(w.project_value_excl_tax or 0.0 for w in blocked_wo_records)
        rec_ids = [str(getattr(w, "source_record_id", w.work_order_id)) for w in blocked_wo_records]
        
        fin_score = calculate_financial_score(blocked_val)
        urgency_score = 95.0 # Blocked projects require immediate unblocking
        severity_score = 90.0
        conf_score = 95.0
        
        total_score = round((fin_score * 0.40) + (urgency_score * 0.30) + (severity_score * 0.20) + (conf_score * 0.10), 1)

        raw_queue_items.append({
            "item_id": "QUEUE-001",
            "title": f"Blocked Execution on {blocked_wo_count} Work Order(s)",
            "description": f"{blocked_wo_count} active Work Order(s) are currently flagged as Blocked, holding {blocked_val:,.2f} INR in contract value.",
            "financial_impact": round(blocked_val, 2),
            "financial_impact_score": fin_score,
            "urgency_score": urgency_score,
            "severity_score": severity_score,
            "confidence_score": conf_score,
            "total_score": total_score,
            "source_board": "Work Orders",
            "source_record_ids": rec_ids,
            "recommended_action": "Schedule immediate operational sync with BD/KAM owner to resolve execution blockers.",
            "why_it_matters": "Blocked execution directly delays billing milestones and risks customer cancellation.",
            "rule_used": "blocked_work_orders_rule"
        })

    # 2. Overdue Active Work Orders Issue
    overdue_wo_count = ops_metrics.get("overdue_work_orders", 0)
    if overdue_wo_count > 0:
        overdue_wo_records = [w for w in work_orders if (getattr(w, "execution_status", "") or "").lower() in ("ongoing", "not started") and w.due_date]
        overdue_val = sum(w.project_value_excl_tax or 0.0 for w in overdue_wo_records)
        rec_ids = [str(getattr(w, "source_record_id", w.work_order_id)) for w in overdue_wo_records]
        
        fin_score = calculate_financial_score(overdue_val)
        urgency_score = 85.0
        severity_score = 80.0
        conf_score = 90.0

        total_score = round((fin_score * 0.40) + (urgency_score * 0.30) + (severity_score * 0.20) + (conf_score * 0.10), 1)

        raw_queue_items.append({
            "item_id": "QUEUE-002",
            "title": f"Schedule Delay on {overdue_wo_count} Overdue Work Order(s)",
            "description": f"{overdue_wo_count} active Work Order(s) have passed their target completion dates without logged delivery.",
            "financial_impact": round(overdue_val, 2),
            "financial_impact_score": fin_score,
            "urgency_score": urgency_score,
            "severity_score": severity_score,
            "confidence_score": conf_score,
            "total_score": total_score,
            "source_board": "Work Orders",
            "source_record_ids": rec_ids,
            "recommended_action": "Review site delivery schedule and re-align delivery dates with client project leads.",
            "why_it_matters": "Unplanned delivery delays breach SLA commitments and erode account trust.",
            "rule_used": "overdue_work_orders_rule"
        })

    # 3. High Customer Concentration Risk Issue
    top_3_pct = pipeline_metrics.get("customer_concentration_top_3", 0.0)
    if top_3_pct > 40.0:
        open_pipe = pipeline_metrics.get("total_open_pipeline", 0.0)
        conc_val = open_pipe * (top_3_pct / 100.0)
        
        fin_score = calculate_financial_score(conc_val)
        urgency_score = 70.0
        severity_score = 85.0
        conf_score = 95.0

        total_score = round((fin_score * 0.40) + (urgency_score * 0.30) + (severity_score * 0.20) + (conf_score * 0.10), 1)

        raw_queue_items.append({
            "item_id": "QUEUE-003",
            "title": f"High Customer Concentration Exposure ({top_3_pct:.1f}% in Top 3 Accounts)",
            "description": f"Top 3 customer accounts represent {top_3_pct:.1f}% of total open pipeline value ({conc_val:,.2f} INR).",
            "financial_impact": round(conc_val, 2),
            "financial_impact_score": fin_score,
            "urgency_score": urgency_score,
            "severity_score": severity_score,
            "confidence_score": conf_score,
            "total_score": total_score,
            "source_board": "Deals",
            "source_record_ids": [],
            "recommended_action": "Diversify mid-funnel prospecting across secondary accounts to reduce key account dependency.",
            "why_it_matters": "High customer concentration creates severe revenue volatility if a key account slips.",
            "rule_used": "customer_concentration_rule"
        })

    # 4. Stale Late-Stage Deals Issue
    stale_count = pipeline_metrics.get("stale_deals", 0)
    if stale_count > 0:
        fin_score = 65.0
        urgency_score = 75.0
        severity_score = 70.0
        conf_score = 85.0

        total_score = round((fin_score * 0.40) + (urgency_score * 0.30) + (severity_score * 0.20) + (conf_score * 0.10), 1)

        raw_queue_items.append({
            "item_id": "QUEUE-004",
            "title": f"Stalled Momentum on {stale_count} Open Deal(s)",
            "description": f"{stale_count} open deals have passed expected close dates or lack close dates altogether.",
            "financial_impact": 0.0,
            "financial_impact_score": fin_score,
            "urgency_score": urgency_score,
            "severity_score": severity_score,
            "confidence_score": conf_score,
            "total_score": total_score,
            "source_board": "Deals",
            "source_record_ids": [],
            "recommended_action": "Require deal owners to update tentative close dates or move dead deals to Lost.",
            "why_it_matters": "Stale pipeline inflates forecasting metrics and hides true revenue performance.",
            "rule_used": "stale_deals_rule"
        })

    # Sort queue items by total_score descending
    sorted_queue = sorted(raw_queue_items, key=lambda x: x["total_score"], reverse=True)

    # Assign priority labels based on rank and score
    for idx, item in enumerate(sorted_queue):
        item["rank"] = idx + 1
        if item["total_score"] >= 80.0:
            item["priority"] = "P1-Critical"
        elif item["total_score"] >= 65.0:
            item["priority"] = "P2-High"
        else:
            item["priority"] = "P3-Medium"

    if evidence_collector:
        for item in sorted_queue:
            evidence_collector.add_evidence(
                metric_name="attention_queue",
                board_name=item["source_board"],
                source_item_id=item["item_id"],
                source_record_id=item["item_id"],
                field_name="total_score",
                raw_value=str(item["total_score"]),
                normalized_value=item["priority"],
                inclusion_reason=f"Priority {item['priority']} item scored {item['total_score']}"
            )

    return sorted_queue
