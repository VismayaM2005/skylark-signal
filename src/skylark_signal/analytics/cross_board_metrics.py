from typing import List, Dict, Any, Optional
from skylark_signal.analytics.evidence import EvidenceCollector
from skylark_signal.analytics.pipeline_metrics import is_won_deal

def build_cross_board_metrics(
    deals: List[Any],
    work_orders: List[Any],
    evidence_collector: Optional[EvidenceCollector] = None
) -> Dict[str, Any]:
    """
    Computes cross-board analytics using customer-level account linkage (shared_customer_match).
    """
    deals_customers = {d.customer for d in deals if d.customer}
    wo_customers = {w.customer for w in work_orders if w.customer}

    shared_customers = deals_customers.intersection(wo_customers)
    shared_customer_accounts_count = len(shared_customers)

    linked_wo = [w for w in work_orders if w.customer in shared_customers]
    unlinked_wo = [w for w in work_orders if w.customer not in shared_customers]
    linked_deals = [d for d in deals if d.customer in shared_customers]

    # Closed Won Deals for customers with ZERO Work Orders
    won_deals = [d for d in deals if is_won_deal(d)]
    customers_with_wo = wo_customers

    won_deals_without_wo = [d for d in won_deals if d.customer not in customers_with_wo]
    wo_without_deals_customers = [w for w in work_orders if w.customer not in deals_customers]

    # Customer-Level Financial Gap (Won Deal Value vs WO Contract Value Excl)
    cust_won_val: Dict[str, float] = {}
    for d in won_deals:
        c = d.customer or "UNKNOWN"
        cust_won_val[c] = cust_won_val.get(c, 0.0) + (d.deal_value or 0.0)

    cust_wo_val: Dict[str, float] = {}
    for w in work_orders:
        c = w.customer or "UNKNOWN"
        cust_wo_val[c] = cust_wo_val.get(c, 0.0) + (w.project_value_excl_tax or 0.0)

    customer_gap: Dict[str, float] = {}
    all_custs = set(cust_won_val.keys()).union(set(cust_wo_val.keys()))
    for c in all_custs:
        won_v = cust_won_val.get(c, 0.0)
        wo_v = cust_wo_val.get(c, 0.0)
        customer_gap[c] = round(won_v - wo_v, 2)

    # Sector Sales vs Execution Gap
    deals_by_sector: Dict[str, float] = {}
    for d in deals:
        sec = getattr(d, "sector", None) or "Unmapped Sector"
        deals_by_sector[sec] = deals_by_sector.get(sec, 0.0) + (d.deal_value or 0.0)

    wo_by_sector: Dict[str, float] = {}
    for w in work_orders:
        sec = getattr(w, "sector", None) or "Unmapped Sector"
        wo_by_sector[sec] = wo_by_sector.get(sec, 0.0) + (w.project_value_excl_tax or 0.0)

    sector_comparison: Dict[str, Dict[str, float]] = {}
    all_sectors = set(deals_by_sector.keys()).union(set(wo_by_sector.keys()))
    for s in all_sectors:
        d_val = deals_by_sector.get(s, 0.0)
        w_val = wo_by_sector.get(s, 0.0)
        sector_comparison[s] = {
            "deals_value": round(d_val, 2),
            "work_orders_value": round(w_val, 2),
            "sales_vs_delivery_gap": round(d_val - w_val, 2)
        }

    if evidence_collector:
        for w in work_orders:
            is_matched = w.customer in shared_customers
            evidence_collector.add_evidence(
                metric_name="shared_customer_match",
                board_name=getattr(w, "source_sheet", "Work Orders"),
                source_item_id=getattr(w, "source_row_number", 0),
                source_record_id=getattr(w, "source_record_id", "UNK"),
                field_name="customer",
                raw_value=str(w.customer),
                normalized_value=w.customer,
                included_in_calculation=is_matched,
                inclusion_reason=f"Customer account {w.customer} matched in Deals board" if is_matched else "Customer account not present in Deals board"
            )

    return {
        "shared_customer_accounts": shared_customer_accounts_count,
        "work_orders_linked_to_shared_customers": len(linked_wo),
        "deals_linked_to_shared_customers": len(linked_linked_deals if 'linked_linked_deals' in locals() else linked_deals),
        "closed_won_deals_without_work_orders": len(won_deals_without_wo),
        "work_orders_without_shared_customer_deals": len(wo_without_deals_customers),
        "customer_level_deal_to_delivery_gap": customer_gap,
        "sector_sales_vs_execution": sector_comparison,
        "match_level_distribution": {
            "shared_customer_match": len(linked_wo),
            "unmatched": len(unlinked_wo),
            "confirmed_record_match": 0 # Explicitly zero (no fabricated record links)
        }
    }
