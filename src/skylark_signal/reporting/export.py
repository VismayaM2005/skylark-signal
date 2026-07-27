import json, csv, io
from typing import Dict, Any
from skylark_signal.reporting.executive_summary import format_leadership_brief_markdown

def export_leadership_brief_markdown(bundle: Dict[str, Any]) -> str:
    """Exports the leadership brief as Markdown text."""
    brief = bundle.get("leadership_brief", {})
    return format_leadership_brief_markdown(brief)

def export_attention_queue_csv(bundle: Dict[str, Any]) -> str:
    """Exports the Founder Attention Queue items as a CSV string."""
    queue = bundle.get("attention_queue", [])
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Rank", "Priority", "Title", "Description", "Financial Impact (INR)",
        "Financial Score", "Urgency Score", "Severity Score", "Confidence Score",
        "Total Score", "Source Board", "Source Record IDs", "Recommended Action", "Why It Matters", "Rule Used"
    ])
    
    for item in queue:
        writer.writerow([
            item.get("rank"),
            item.get("priority"),
            item.get("title"),
            item.get("description"),
            item.get("financial_impact"),
            item.get("financial_impact_score"),
            item.get("urgency_score"),
            item.get("severity_score"),
            item.get("confidence_score"),
            item.get("total_score"),
            item.get("source_board"),
            "; ".join(item.get("source_record_ids", [])),
            item.get("recommended_action"),
            item.get("why_it_matters"),
            item.get("rule_used")
        ])
        
    return output.getvalue()

def export_evidence_bundle_csv(bundle: Dict[str, Any]) -> str:
    """Exports evidence counts and risk item evidence as a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Metric / Risk Category", "Included Evidence Count"])
    counts = bundle.get("evidence_counts", {})
    for metric, count in counts.items():
        writer.writerow([metric, count])
        
    return output.getvalue()

def export_analytics_snapshot_json(bundle: Dict[str, Any]) -> str:
    """Exports the full analytics bundle dictionary as a JSON string."""
    return json.dumps(bundle, indent=2)
