import os, sys, json
# Add src directory to path
sys.path.insert(0, os.path.abspath("src"))

from skylark_signal.config import config
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.data.repository import MondayRepository
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.reporting import format_leadership_brief_markdown

def load_canonical_from_json(json_path: str, model_cls):
    """Loads a list of canonical Pydantic models from a processed JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [model_cls(**item) for item in data]

def main():
    print("=== SKYLARK SIGNAL DETERMINISTIC ANALYTICS GENERATOR ===")
    
    deals_json_path = "data/processed/deals_clean.json"
    wo_json_path = "data/processed/work_orders_clean.json"

    token_set = bool(config.monday_api_token and config.monday_deals_board_id and config.monday_work_orders_board_id)

    if token_set:
        print("Connecting to live monday.com API via MondayRepository...")
        try:
            repo = MondayRepository()
            deals_snap = repo.fetch_deals_snapshot()
            wo_snap = repo.fetch_work_orders_snapshot()
            deals = deals_snap.canonical_records
            work_orders = wo_snap.canonical_records
            print(f"Loaded {len(deals)} deals and {len(work_orders)} work orders from live API.")
        except Exception as e:
            print(f"Live API connection failed: {e}. Falling back to processed JSON datasets...\n")
            deals = load_canonical_from_json(deals_json_path, CanonicalDealRecord)
            work_orders = load_canonical_from_json(wo_json_path, CanonicalWorkOrderRecord)
    else:
        print("Loading processed clean JSON datasets from data/processed/...")
        deals = load_canonical_from_json(deals_json_path, CanonicalDealRecord)
        work_orders = load_canonical_from_json(wo_json_path, CanonicalWorkOrderRecord)

    print(f"Processing {len(deals)} canonical Deal records and {len(work_orders)} Work Order records...")

    # Build Full Analytics Bundle
    bundle = build_full_analytics_bundle(deals, work_orders)

    # Export analytics_snapshot.json
    out_snapshot_path = "data/processed/analytics_snapshot.json"
    with open(out_snapshot_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)
    print(f"[OK] Exported analytics snapshot to {out_snapshot_path}")

    # Export leadership_brief.md
    brief_md = format_leadership_brief_markdown(bundle["leadership_brief"])
    out_brief_path = "data/processed/leadership_brief.md"
    with open(out_brief_path, "w", encoding="utf-8") as f:
        f.write(brief_md)
    print(f"[OK] Exported leadership brief to {out_brief_path}\n")

    # Display Console Summary
    p_m = bundle["pipeline_metrics"]
    o_m = bundle["operations_metrics"]
    cb_m = bundle["cross_board_metrics"]
    r_m = bundle["revenue_at_risk"]
    t_m = bundle["data_trust_score"]

    print("--------------------------------------------------")
    print("MAIN PIPELINE METRICS (DEALS):")
    print(f"  Total Deals: {p_m['total_deals']} | Open: {p_m['open_deals']} | Won: {p_m['won_deals']} | Lost: {p_m['lost_deals']}")
    print(f"  Total Open Pipeline: INR {p_m['total_open_pipeline']:,.2f}")
    print(f"  Weighted Open Pipeline: INR {p_m['weighted_pipeline']:,.2f}")
    print(f"  Win Rate: {p_m['win_rate']*100:.1f}% | Pipeline Quality Score: {p_m['pipeline_quality_score']:.1f}/100")
    print(f"  Top 3 Customer Concentration: {p_m['customer_concentration_top_3']:.1f}%")

    print("\nMAIN OPERATIONS METRICS (WORK ORDERS):")
    print(f"  Total Work Orders: {o_m['total_work_orders']} | Active: {o_m['active_work_orders']} | Completed: {o_m['completed_work_orders']}")
    print(f"  Blocked: {o_m['blocked_work_orders']} | Delayed: {o_m['delayed_work_orders']} | Overdue: {o_m['overdue_work_orders']}")
    print(f"  Average Project Value: INR {o_m['average_project_value']:,.2f} | Operations Quality Score: {o_m['operations_quality_score']:.1f}/100")

    print("\nCROSS-BOARD MATCH SUMMARY:")
    print(f"  Shared Customer Accounts: {cb_m['shared_customer_accounts']}")
    print(f"  Work Orders Linked to Shared Customers: {cb_m['work_orders_linked_to_shared_customers']}")
    print(f"  Match Level: shared_customer_match ({cb_m['work_orders_linked_to_shared_customers']} WO), confirmed_record_match (0)")

    print("\nREVENUE AT RISK SUMMARY:")
    print(f"  Total Revenue at Risk: INR {r_m['total_revenue_at_risk']:,.2f}")
    for k, v in r_m['risk_breakdown_by_category'].items():
        print(f"    - {k}: INR {v:,.2f}")

    print("\nTOP FOUNDER ATTENTION ITEMS:")
    for item in bundle["attention_queue"][:3]:
        print(f"  [{item['priority']}] Rank #{item['rank']}: {item['title']} (Score: {item['total_score']})")

    print("\nDATA TRUST SCORE:")
    print(f"  Combined Data Trust Score: {t_m['combined_trust_score']}/100 [{t_m['trust_rating']}]")

    print("\n=== ANALYTICS SNAPSHOT GENERATION COMPLETE ===")

if __name__ == "__main__":
    main()
