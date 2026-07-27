from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from skylark_signal.analytics.evidence import EvidenceCollector
from skylark_signal.analytics.pipeline_metrics import build_pipeline_metrics
from skylark_signal.analytics.operations_metrics import build_operations_metrics
from skylark_signal.analytics.cross_board_metrics import build_cross_board_metrics
from skylark_signal.analytics.risk import build_revenue_at_risk
from skylark_signal.analytics.attention_queue import build_attention_queue
from skylark_signal.reporting.data_trust import build_data_trust_score
from skylark_signal.analytics.leadership import build_leadership_brief
from skylark_signal.reporting.executive_summary import format_leadership_brief_markdown

def build_full_analytics_bundle(
    deals: List[Any],
    work_orders: List[Any]
) -> Dict[str, Any]:
    """
    Master orchestration function that generates all deterministic analytics, risk models,
    attention queue items, leadership brief, data trust scores, and evidence bundles.
    """
    collector = EvidenceCollector()

    # 1. Pipeline Metrics
    p_metrics = build_pipeline_metrics(deals, evidence_collector=collector)

    # 2. Operations Metrics
    o_metrics = build_operations_metrics(work_orders, evidence_collector=collector)

    # 3. Cross-Board Metrics
    cb_metrics = build_cross_board_metrics(deals, work_orders, evidence_collector=collector)

    # 4. Revenue at Risk Engine
    risk_bundle = build_revenue_at_risk(deals, work_orders, evidence_collector=collector)

    # 5. Founder Attention Queue
    att_queue = build_attention_queue(
        deals, work_orders, risk_bundle, p_metrics, o_metrics, cb_metrics, evidence_collector=collector
    )

    # 6. Data Trust Score
    trust_score = build_data_trust_score(deals, work_orders)

    # 7. Leadership Brief
    lead_brief = build_leadership_brief(
        deals, work_orders, p_metrics, o_metrics, cb_metrics, risk_bundle, att_queue, trust_score
    )

    # 8. Evidence Counts
    evidence_counts = collector.count_by_metric()

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "deals_count": len(deals),
            "work_orders_count": len(work_orders),
            "total_evidence_records": len(collector.get_all_evidence())
        },
        "pipeline_metrics": p_metrics,
        "operations_metrics": o_metrics,
        "cross_board_metrics": cb_metrics,
        "revenue_at_risk": risk_bundle,
        "attention_queue": att_queue,
        "data_trust_score": trust_score,
        "leadership_brief": lead_brief,
        "evidence_counts": evidence_counts
    }
