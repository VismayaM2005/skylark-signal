# Skylark Signal - Architecture & Executive Decision Log

**Project Name**: Skylark Signal  
**Target Platform**: monday.com Deals & Work Orders Boards  
**Version**: 1.0.0 (Production Release)  
**Date**: July 27, 2026  

---

## 1. Executive Summary & Product Vision

Skylark Signal is built as a **founder-facing decision cockpit** for monday.com sales and delivery operations. Unlike generic "chat with data" wrappers that rely on LLMs to perform arithmetic (introducing hallucination risks), Skylark Signal enforces a strict **separation of concerns**:
- **Deterministic Intelligence Core**: 100% verified Python calculation of pipeline metrics, delivery bottlenecks, revenue at risk, and multi-dimensional attention queue scores.
- **AI Phrasing Layer**: LLMs (OpenRouter / OpenAI) are used exclusively for text phrasing, intent interpretation, and response polishing.
- **Traceable Micro-Evidence**: Every metric, score, and recommendation is linked to underlying canonical source record IDs and explicit mathematical formulas.

---

## 2. Key Technical & Data Assumptions

1. **Work Order Canonical Identifier**:
   - `Serial #` in the raw Work Orders Excel dataset is canonical `work_order_id` (e.g. `SDPLDEAL-001`).
   - `deal_reference` remains `None` unless an explicit source field proves a 1-to-1 relationship with a specific Deal.
2. **Account-Level Linkage vs. Record-Level Joins**:
   - Customer Code normalization links 175 of 176 Work Orders at the **customer account level** (99.43% coverage).
   - A shared customer code proves that a Work Order and a Deal belong to the same client, but does *not* prove which specific Deal generated the Work Order.
3. **Date & Text Canonicalization Rules**:
   - Mixed date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`) and financial quarter text (`Q1 FY25`, `Q3 2024`) are parsed into ISO 8601 strings.
   - Ambiguous day-first dates (e.g. `05-04-2024`) are deterministically parsed as Day-First (`YYYY-04-05`) per Indian business convention. Unparseable dates remain `None` with data quality warning flags without silent imputation.
4. **Mutually Exclusive Revenue at Risk**:
   - Risk categories are strictly non-overlapping (Overdue Active Work Orders, Stale Late-Stage Deals, High-Value Missing Probability Deals) to guarantee **zero double-counting** of risk exposure.
5. **Stale Deal Threshold**:
   - A deal is flagged as *stale* if it has been inactive for > 60 days past its tentative close date or lacks a close date entirely.

---

## 3. Key Architectural Trade-Offs & Rationale

| Architecture Decision | Chosen Approach | Alternative Considered | Rationale |
| :--- | :--- | :--- | :--- |
| **Calculation Engine** | Pure Python Deterministic Formulas | LLM-Driven Code Execution / Text-to-SQL | Eliminates metric hallucinations; provides 100% auditability for executive reporting. |
| **Data Ingestion** | Live monday.com GraphQL API with Offline JSON Fallback | Live API Only | Ensures the app is 100% operational even without active API credentials or internet access. |
| **LLM Provider Strategy** | OpenRouter + OpenAI + Deterministic Fallback | Single Fixed Model (e.g. GPT-4o only) | Gives founders choice over model selection while guaranteeing full functionality with 0 API keys. |
| **State Management** | Deep-Copy In-Memory Scenario Engine | Direct DB / Board State Mutation | Prevents hypothetical scenario simulations from corrupting actual baseline board records. |

---

## 4. Interpretation of "Leadership Updates"

In Skylark Signal, a **Leadership Update** is interpreted as an executive-ready briefing designed for immediate action in weekly founder syncs:
- **Business Health Badge**: Overall indicator (`GREEN`, `AMBER`, `RED`) derived deterministically from pipeline velocity and operational bottleneck counts.
- **Executive Pulse**: Direct 2-sentence narrative summarizing revenue momentum versus operational delivery delays.
- **Five Numbers to Quote**: Key metrics formatted for executive recall (Open Pipeline, Weighted Pipeline, Revenue at Risk, Active Work Orders, Data Trust Score).
- **Top Wins vs. Top Risks**: Categorized summary contrasting sales achievements with active operational threats.
- **Decisions Required**: Concrete action items specifying required leadership interventions.

---

## 5. Future Roadmap: What We Would Do Differently With More Time

1. **Formal Record-Level Relational Column**: Add a native monday.com `Board Relation` column linking individual Work Orders directly to their originating Deal item ID.
2. **Automated Webhook Subscriptions**: Implement monday.com webhook listeners for instant, real-time board mutation events instead of poll-based snapshot fetching.
3. **Automated E-mail / Slack Leadership Pulse**: Schedule automated weekly leadership briefs pushed directly to Slack channels or founder email inboxes via SendGrid / Webhooks.
