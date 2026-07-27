from typing import Dict, Any

def format_leadership_brief_markdown(brief: Dict[str, Any]) -> str:
    """Formats a leadership brief dictionary into clean, presentation-ready Markdown."""
    status_emoji = "🟢" if brief["overall_status"] == "GREEN" else ("🟡" if brief["overall_status"] == "AMBER" else "🔴")
    
    lines = []
    lines.append(f"# Skylark Signal - Founder Leadership Brief")
    lines.append(f"**Overall Business Status**: {status_emoji} **`{brief['overall_status']}`**  ")
    lines.append(f"**Generated**: `{brief['generation_timestamp']}`  \n")
    lines.append(f"---")
    lines.append(f"## 1. Executive Pulse")
    lines.append(f"> {brief['executive_pulse']}\n")

    lines.append(f"## 2. Five Numbers to Quote")
    for num in brief["five_numbers_to_quote"]:
        lines.append(f"- **{num['label']}**: `{num['value']}`")
    lines.append("")

    lines.append(f"## 3. Top Wins & Strengths")
    for win in brief["top_wins"]:
        lines.append(f"- ✓ {win}")
    lines.append("")

    lines.append(f"## 4. Top Risks & Bottlenecks")
    for risk in brief["top_risks"]:
        lines.append(f"- ⚠️ {risk}")
    lines.append("")

    lines.append(f"## 5. Pipeline & Execution Summaries")
    lines.append(f"### Deals & Sales Pipeline")
    lines.append(f"{brief['pipeline_summary']}\n")
    lines.append(f"### Operations & Delivery")
    lines.append(f"{brief['execution_summary']}\n")
    lines.append(f"### Revenue at Risk")
    lines.append(f"{brief['revenue_at_risk_summary']}\n")

    lines.append(f"## 6. Decisions Required")
    for dec in brief["decisions_required"]:
        lines.append(f"1. {dec}")
    lines.append("")

    lines.append(f"## 7. Recommended Next Actions")
    for act in brief["recommended_actions"]:
        lines.append(f"- [ ] {act}")
    lines.append("")

    lines.append(f"## 8. Data Trust & Quality")
    lines.append(f"{brief['data_trust_summary']}")

    return "\n".join(lines)
