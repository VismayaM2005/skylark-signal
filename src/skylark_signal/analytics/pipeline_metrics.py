from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timezone
from skylark_signal.config import config
from skylark_signal.analytics.evidence import EvidenceCollector

def is_open_deal(d: Any) -> bool:
    """Checks if a deal record is currently open."""
    status = getattr(d, "status", "") or ""
    stage = getattr(d, "stage", "") or ""
    status_lower = status.lower()
    stage_lower = stage.lower()

    if status_lower in ("won", "closed won", "dead", "lost", "closed lost"):
        return False
    if "project won" in stage_lower or "project lost" in stage_lower or "dead" in stage_lower:
        return False
    return True

def is_won_deal(d: Any) -> bool:
    """Checks if a deal record is closed won."""
    status = getattr(d, "status", "") or ""
    stage = getattr(d, "stage", "") or ""
    return status.lower() in ("won", "closed won") or "project won" in stage.lower()

def is_lost_deal(d: Any) -> bool:
    """Checks if a deal record is closed lost/dead."""
    status = getattr(d, "status", "") or ""
    stage = getattr(d, "stage", "") or ""
    return status.lower() in ("dead", "lost", "closed lost") or "project lost" in stage.lower() or "dead" in stage.lower()

def build_pipeline_metrics(
    deals: List[Any],
    evidence_collector: Optional[EvidenceCollector] = None
) -> Dict[str, Any]:
    """
    Computes deterministic sales pipeline and funnel metrics from canonical deal records.
    """
    total_deals = len(deals)
    open_deals_list = [d for d in deals if is_open_deal(d)]
    won_deals_list = [d for d in deals if is_won_deal(d)]
    lost_deals_list = [d for d in deals if is_lost_deal(d)]

    open_deals_count = len(open_deals_list)
    won_deals_count = len(won_deals_list)
    lost_deals_count = len(lost_deals_list)

    # 1. Pipeline Financial Totals
    open_values = [d.deal_value for d in open_deals_list if d.deal_value is not None]
    total_open_pipeline = float(sum(open_values))

    weighted_values = []
    for d in open_deals_list:
        if d.deal_value is not None and d.probability is not None:
            w_val = d.deal_value * d.probability
            weighted_values.append(w_val)
            if evidence_collector:
                evidence_collector.add_evidence(
                    metric_name="weighted_pipeline",
                    board_name=getattr(d, "source_sheet", "Deals"),
                    source_item_id=getattr(d, "source_row_number", 0),
                    source_record_id=getattr(d, "source_record_id", "UNK"),
                    field_name="deal_value * probability",
                    raw_value=str(d.deal_value),
                    normalized_value=w_val,
                    inclusion_reason=f"Calculated weighted value: {d.deal_value} * {d.probability} = {w_val}"
                )

    weighted_pipeline = float(sum(weighted_values))

    # 2. Stage and Sector Distributions (Open Deals)
    pipeline_by_stage: Dict[str, float] = {}
    for d in open_deals_list:
        stg = getattr(d, "stage", "Unmapped Stage") or "Unmapped Stage"
        val = d.deal_value or 0.0
        pipeline_by_stage[stg] = round(pipeline_by_stage.get(stg, 0.0) + val, 2)

    pipeline_by_sector: Dict[str, float] = {}
    for d in open_deals_list:
        sec = getattr(d, "sector", "Unmapped Sector") or "Unmapped Sector"
        val = d.deal_value or 0.0
        pipeline_by_sector[sec] = round(pipeline_by_sector.get(sec, 0.0) + val, 2)

    # 3. Statistical Averages & Medians (All Deals with Values)
    all_values = [d.deal_value for d in deals if d.deal_value is not None]
    average_deal_value = float(np.mean(all_values)) if all_values else 0.0
    median_deal_value = float(np.median(all_values)) if all_values else 0.0

    win_denom = won_deals_count + lost_deals_count
    win_rate = round(won_deals_count / win_denom, 4) if win_denom > 0 else 0.0

    # 4. Data Quality & Completeness Counters
    deals_missing_close_date_list = [d for d in open_deals_list if d.expected_close_date is None and d.expected_close_period is None]
    deals_missing_prob_list = [d for d in open_deals_list if d.probability is None]
    deals_missing_owner_list = [d for d in deals if not d.owner]

    deals_missing_close_date_count = len(deals_missing_close_date_list)
    deals_missing_prob_count = len(deals_missing_prob_list)
    deals_missing_owner_count = len(deals_missing_owner_list)

    # 5. Stale Deals & Quarter Filtering
    ref_date_str = config.reference_date_iso or "2026-07-27"
    try:
        ref_dt = datetime.strptime(ref_date_str, "%Y-%m-%d")
    except Exception:
        ref_dt = datetime.now()

    stale_deals_list = []
    expected_this_quarter_list = []

    for d in open_deals_list:
        # Check quarter text e.g. Q3 FY26
        period_str = str(getattr(d, "expected_close_period", "") or "").upper()
        if "Q3" in period_str or "FY26" in period_str:
            expected_this_quarter_list.append(d)

        # Check stale criteria: missing close date OR expected date in the past relative to ref_dt
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
            stale_deals_list.append(d)

    # 6. Customer & Sector Concentration Ratios (Open Pipeline Value)
    cust_pipeline: Dict[str, float] = {}
    for d in open_deals_list:
        c_code = d.customer or "UNKNOWN"
        cust_pipeline[c_code] = cust_pipeline.get(c_code, 0.0) + (d.deal_value or 0.0)

    sorted_cust_values = sorted(cust_pipeline.values(), reverse=True)
    top_3_sum = sum(sorted_cust_values[:3])
    top_5_sum = sum(sorted_cust_values[:5])

    customer_concentration_top_3 = round(top_3_sum / total_open_pipeline * 100.0, 2) if total_open_pipeline > 0 else 0.0
    customer_concentration_top_5 = round(top_5_sum / total_open_pipeline * 100.0, 2) if total_open_pipeline > 0 else 0.0

    sector_vals = list(pipeline_by_sector.values())
    max_sector_val = max(sector_vals) if sector_vals else 0.0
    sector_concentration = round(max_sector_val / total_open_pipeline * 100.0, 2) if total_open_pipeline > 0 else 0.0

    # 7. Pipeline Quality Score (0-100)
    val_completeness = (len(open_values) / open_deals_count * 100.0) if open_deals_count > 0 else 100.0
    prob_completeness = ((open_deals_count - deals_missing_prob_count) / open_deals_count * 100.0) if open_deals_count > 0 else 100.0
    date_completeness = ((open_deals_count - deals_missing_close_date_count) / open_deals_count * 100.0) if open_deals_count > 0 else 100.0

    pipeline_quality_score = round((val_completeness * 0.40) + (prob_completeness * 0.35) + (date_completeness * 0.25), 1)

    if evidence_collector:
        for d in open_deals_list:
            evidence_collector.add_evidence(
                metric_name="total_open_pipeline",
                board_name=getattr(d, "source_sheet", "Deals"),
                source_item_id=getattr(d, "source_row_number", 0),
                source_record_id=getattr(d, "source_record_id", "UNK"),
                field_name="deal_value",
                raw_value=str(d.deal_value),
                normalized_value=d.deal_value,
                included_in_calculation=d.deal_value is not None,
                inclusion_reason="Open deal with valid deal_value" if d.deal_value is not None else "Excluded: Missing deal_value"
            )

    return {
        "total_deals": total_deals,
        "open_deals": open_deals_count,
        "won_deals": won_deals_count,
        "lost_deals": lost_deals_count,
        "total_open_pipeline": total_open_pipeline,
        "weighted_pipeline": weighted_pipeline,
        "pipeline_by_stage": pipeline_by_stage,
        "pipeline_by_sector": pipeline_by_sector,
        "average_deal_value": round(average_deal_value, 2),
        "median_deal_value": round(median_deal_value, 2),
        "win_rate": win_rate,
        "deals_expected_to_close_this_quarter": len(expected_this_quarter_list),
        "stale_deals": len(stale_deals_list),
        "deals_missing_close_date": deals_missing_close_date_count,
        "deals_missing_probability": deals_missing_prob_count,
        "deals_missing_owner": deals_missing_owner_count,
        "customer_concentration_top_3": customer_concentration_top_3,
        "customer_concentration_top_5": customer_concentration_top_5,
        "sector_concentration": sector_concentration,
        "pipeline_quality_score": pipeline_quality_score
    }
