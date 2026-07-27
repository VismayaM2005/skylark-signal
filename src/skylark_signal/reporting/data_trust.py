from typing import List, Dict, Any, Optional

def build_data_trust_score(
    deals: List[Any],
    work_orders: List[Any]
) -> Dict[str, Any]:
    """
    Computes a deterministic Data Trust Score (0-100) for Deals, Work Orders, and Combined datasets.
    """
    n_deals = len(deals)
    n_wo = len(work_orders)

    # 1. Deals Board Trust Components
    if n_deals > 0:
        d_val_comp = sum(1 for d in deals if d.deal_value is not None) / n_deals
        d_prob_comp = sum(1 for d in deals if d.probability is not None) / n_deals
        d_date_comp = sum(1 for d in deals if d.expected_close_date is not None or d.expected_close_period is not None) / n_deals
        d_cat_comp = sum(1 for d in deals if d.stage != "Unmapped Stage" and d.status != "Open") / n_deals
        
        deals_score = round(((d_val_comp * 0.35) + (d_prob_comp * 0.25) + (d_date_comp * 0.20) + (d_cat_comp * 0.20)) * 100.0, 1)
    else:
        deals_score = 0.0

    # 2. Work Orders Board Trust Components
    if n_wo > 0:
        w_id_comp = sum(1 for w in work_orders if w.work_order_id and not w.work_order_id.startswith("WO-ROW-")) / n_wo
        w_val_comp = sum(1 for w in work_orders if w.project_value_excl_tax is not None) / n_wo
        w_date_comp = sum(1 for w in work_orders if w.due_date is not None or w.completion_date is not None) / n_wo
        w_cust_comp = sum(1 for w in work_orders if w.customer and w.customer != "COMPANY_UNKNOWN") / n_wo
        
        wo_score = round(((w_id_comp * 0.30) + (w_val_comp * 0.30) + (w_date_comp * 0.20) + (w_cust_comp * 0.20)) * 100.0, 1)
    else:
        wo_score = 0.0

    # 3. Combined Trust Score & Account Coverage
    deals_custs = {d.customer for d in deals if d.customer}
    wo_custs = {w.customer for w in work_orders if w.customer}
    shared_custs = deals_custs.intersection(wo_custs)
    
    account_match_ratio = (len(shared_custs) / len(wo_custs)) if wo_custs else 1.0
    
    combined_score = round((deals_score * 0.45) + (wo_score * 0.45) + (account_match_ratio * 100.0 * 0.10), 1)

    # 4. Rating Assignment
    if combined_score >= 85.0:
        rating = "HIGH TRUST (EXCELLENT)"
    elif combined_score >= 70.0:
        rating = "MODERATE TRUST (GOOD)"
    elif combined_score >= 50.0:
        rating = "FAIR TRUST (WARNING)"
    else:
        rating = "LOW TRUST (POOR)"

    warning_flags = []
    if d_prob_comp < 0.50 if n_deals > 0 else False:
        warning_flags.append(f"Low closure probability coverage in Deals ({d_prob_comp*100:.1f}%)")
    if d_val_comp < 0.60 if n_deals > 0 else False:
        warning_flags.append(f"Missing deal values in Deals ({(1-d_val_comp)*100:.1f}% missing)")
    if account_match_ratio < 0.90:
        warning_flags.append(f"Unmatched Work Order customer accounts ({(1-account_match_ratio)*100:.1f}% unmatched)")

    return {
        "combined_trust_score": combined_score,
        "trust_rating": rating,
        "deals_board_score": deals_score,
        "work_orders_board_score": wo_score,
        "account_match_coverage_score": round(account_match_ratio * 100.0, 1),
        "component_scores": {
            "deals_value_completeness": round(d_val_comp * 100.0, 1) if n_deals > 0 else 0.0,
            "deals_probability_completeness": round(d_prob_comp * 100.0, 1) if n_deals > 0 else 0.0,
            "deals_date_completeness": round(d_date_comp * 100.0, 1) if n_deals > 0 else 0.0,
            "work_orders_id_validity": round(w_id_comp * 100.0, 1) if n_wo > 0 else 0.0,
            "work_orders_value_completeness": round(w_val_comp * 100.0, 1) if n_wo > 0 else 0.0,
            "work_orders_date_completeness": round(w_date_comp * 100.0, 1) if n_wo > 0 else 0.0
        },
        "warning_flags": warning_flags,
        "excluded_record_counts": {
            "deals_excluded_from_metrics": sum(1 for d in deals if getattr(d, "excluded_from_metrics", False)),
            "work_orders_excluded_from_metrics": sum(1 for w in work_orders if getattr(w, "excluded_from_metrics", False))
        }
    }
