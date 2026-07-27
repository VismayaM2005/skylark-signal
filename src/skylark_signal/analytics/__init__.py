"""Analytics subpackage for Skylark Signal."""
from skylark_signal.analytics.pipeline import build_full_analytics_bundle
from skylark_signal.analytics.pipeline_metrics import build_pipeline_metrics
from skylark_signal.analytics.operations_metrics import build_operations_metrics
from skylark_signal.analytics.cross_board_metrics import build_cross_board_metrics
from skylark_signal.analytics.risk import build_revenue_at_risk
from skylark_signal.analytics.attention_queue import build_attention_queue
from skylark_signal.analytics.leadership import build_leadership_brief
from skylark_signal.analytics.evidence import EvidenceCollector, EvidenceRecord

__all__ = [
    "build_full_analytics_bundle",
    "build_pipeline_metrics",
    "build_operations_metrics",
    "build_cross_board_metrics",
    "build_revenue_at_risk",
    "build_attention_queue",
    "build_leadership_brief",
    "EvidenceCollector",
    "EvidenceRecord"
]
