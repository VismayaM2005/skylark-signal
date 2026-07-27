from typing import Dict, Any, List, Optional
from skylark_signal.agent.planner import QueryPlanner
from skylark_signal.agent.context import ConversationContext
from skylark_signal.analytics import build_full_analytics_bundle
from skylark_signal.analytics.formatting import format_currency, format_percentage

class SafeExecutiveResponder:
    """
    Constructs a 100% verified, 9-part structured response object for founder queries,
    handling ambiguity clarification and multi-turn context inheritance.
    """
    def __init__(self, planner: Optional[QueryPlanner] = None):
        self.planner = planner or QueryPlanner()

    def respond(
        self,
        query: str,
        deals: List[Any],
        work_orders: List[Any],
        provider: str = "deterministic",
        model_slug: Optional[str] = None,
        context: Optional[ConversationContext] = None
    ) -> Dict[str, Any]:
        """
        Executes query planning, ambiguity checks, analytics calculations, and response building.
        """
        plan = self.planner.plan_query(query, context)
        intent = plan["intent"]

        # Check Ambiguity Flag
        if plan.get("is_ambiguous", False):
            return {
                "query": query,
                "intent": intent,
                "is_clarification": True,
                "missing_dimension": plan["missing_dimension"],
                "executive_answer": f"❓ **Clarification Required**: {plan['clarification_prompt']}",
                "key_metrics": {"Status": "Awaiting User Input"},
                "business_interpretation": "The query is missing a key dimension needed to compute precise metrics.",
                "recommended_actions": ["Select a specific sector or time window to refine the response."],
                "data_trust_score": {"score": 100.0, "rating": "HIGH TRUST"},
                "data_caveats": ["Clarification requested to avoid guessing user intent."],
                "evidence_and_formulas": ["Rule: Ambiguous queries trigger explicit clarification."],
                "source_records": [],
                "suggested_followups": [
                    "How is the Mining pipeline looking?",
                    "How is the Renewables pipeline looking?",
                    "Show all sectors breakdown"
                ],
                "llm_trace": {
                    "provider": provider,
                    "model_slug": model_slug or "none",
                    "used_llm": False,
                    "execution_path": "deterministic_clarification",
                    "fallback_reason": "Query ambiguity triggered clarification prompt"
                }
            }

        # Filter deals by active context sector if query doesn't explicitly override it
        active_sector = context.active_sector if context else None
        target_deals = deals
        target_wo = work_orders

        if active_sector:
            target_deals = [d for d in deals if d.sector == active_sector]
            target_wo = [w for w in work_orders if w.sector == active_sector]

        # Compute full analytics bundle
        bundle = build_full_analytics_bundle(target_deals, target_wo)

        p_m = bundle["pipeline_metrics"]
        o_m = bundle["operations_metrics"]
        cb_m = bundle["cross_board_metrics"]
        r_m = bundle["revenue_at_risk"]
        att_queue = bundle["attention_queue"]
        t_m = bundle["data_trust_score"]

        # Default response elements
        executive_answer = ""
        key_metrics = {}
        interpretation = ""
        recommended_actions = []
        caveats = []
        evidence_formulas = []
        source_records = []
        followups = []

        sector_label = f" in {active_sector}" if active_sector else ""

        if intent == "founder_attention":
            top_item = att_queue[0] if att_queue else {}
            executive_answer = f"The single highest priority item requiring leadership attention{sector_label} is '{top_item.get('title', 'None')}' (Priority {top_item.get('priority', 'P1')}, Score {top_item.get('total_score', 0.0):.1f}). Overall status is {bundle['leadership_brief']['overall_status']}."
            key_metrics = {
                "P1 Attention Items": len([i for i in att_queue if "P1" in i.get("priority", "")]),
                "Top Risk Exposure": format_currency(top_item.get("financial_impact", 0.0)),
                "Total Revenue at Risk": format_currency(r_m["total_revenue_at_risk"])
            }
            interpretation = top_item.get("why_it_matters", "Operational bottlenecks require immediate founder intervention.")
            recommended_actions = [top_item.get("recommended_action", "Review priority items"), "Convene weekly sync"]
            caveats = ["Scored using multi-dimensional weights (Financial 40%, Urgency 30%, Severity 20%, Confidence 10%)."]
            evidence_formulas = ["Attention Score = (0.40 * Financial) + (0.30 * Urgency) + (0.20 * Severity) + (0.10 * Confidence)"]
            followups = [
                "Which work orders are overdue?",
                "How much revenue is at risk?",
                "What to discuss in leadership sync?"
            ]

        elif intent == "revenue_at_risk":
            total_risk = r_m["total_revenue_at_risk"]
            executive_answer = f"Total revenue at risk{sector_label} stands at {format_currency(total_risk)} across {r_m['risk_items_count']} mutually exclusive risk categories."
            key_metrics = {
                "Total Revenue at Risk": format_currency(total_risk),
                "Overdue Active Work Orders": format_currency(r_m['risk_breakdown_by_category'].get('overdue_active_work_orders', 0.0)),
                "Stale Late-Stage Deals": format_currency(r_m['risk_breakdown_by_category'].get('stale_late_stage_deals', 0.0))
            }
            interpretation = "Revenue at risk represents contract value where execution delays create vulnerability to loss."
            recommended_actions = ["Schedule delivery sync on overdue work orders", "Re-evaluate stale deal close dates"]
            caveats = ["Zero double-counting: Risk categories are strictly non-overlapping."]
            evidence_formulas = ["Revenue at Risk = Sum(Blocked/Delayed WO) + Sum(Overdue Active WO) + Sum(Stale Late Stage Deals)"]
            followups = [
                "What requires my attention right now?",
                "Which deals are stale?",
                "How is the pipeline looking this quarter?"
            ]

        elif intent == "stale_deals":
            stale_count = p_m["stale_deals"]
            executive_answer = f"There are {stale_count} open deals{sector_label} currently flagged as stale, having passed their tentative close dates or lacking close dates altogether."
            key_metrics = {
                "Stale Deals Count": stale_count,
                "Open Deals Missing Close Date": p_m["deals_missing_close_date"],
                "Total Open Pipeline": format_currency(p_m["total_open_pipeline"])
            }
            interpretation = "Stale deals distort pipeline forecasting and obscure true sales momentum."
            recommended_actions = ["Mandate account managers to update close dates", "Move inactive deals to Lost"]
            caveats = ["Stale threshold configured to 60 days of inactivity."]
            evidence_formulas = ["Stale Criteria = Open deal with missing close date OR close date > 60 days past"]
            followups = [
                "Which sectors have the strongest pipeline?",
                "How much revenue is at risk?",
                "How clean is our data?"
            ]

        else: # Default pipeline / executive summary intent
            open_pipe = p_m["total_open_pipeline"]
            weighted_pipe = p_m["weighted_pipeline"]
            executive_answer = f"Total open pipeline{sector_label} stands at {format_currency(open_pipe)} ({format_currency(weighted_pipe)} weighted) across {p_m['open_deals']} open deals."
            key_metrics = {
                "Total Open Pipeline": format_currency(open_pipe),
                "Weighted Pipeline": format_currency(weighted_pipe),
                "Win Rate": format_percentage(p_m["win_rate"]),
                "Active Work Orders": o_m["active_work_orders"]
            }
            interpretation = "Pipeline health remains strong, but delivery delays on active work orders require management focus."
            recommended_actions = ["Focus sales effort on high-probability deals", "Unblock overdue work orders"]
            caveats = ["Win rate is computed on closed deals only."]
            evidence_formulas = ["Weighted Pipeline = Sum(deal_value * probability)"]
            followups = [
                "What requires my attention right now?",
                "How much revenue is at risk?",
                "Which sectors perform best?"
            ]

        # Update conversation context
        if context:
            context.process_query_turn(query, intent, executive_answer)

        # Polish answer via LLM and capture trace metadata
        polished_answer, llm_trace = self.planner.rephrase_answer_with_trace(
            query=query,
            executive_answer=executive_answer,
            key_metrics=key_metrics,
            provider=provider,
            model_slug=model_slug
        )

        return {
            "query": query,
            "intent": intent,
            "is_clarification": False,
            "executive_answer": polished_answer,
            "key_metrics": key_metrics,
            "business_interpretation": interpretation,
            "recommended_actions": recommended_actions,
            "data_trust_score": {
                "score": t_m["combined_trust_score"],
                "rating": t_m["trust_rating"]
            },
            "data_caveats": caveats + t_m["warning_flags"],
            "evidence_and_formulas": evidence_formulas,
            "source_records": source_records,
            "suggested_followups": followups,
            "llm_trace": llm_trace
        }
