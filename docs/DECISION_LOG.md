# Skylark Signal - Architecture & Executive Decision Log

**Project Name**: Skylark Signal | **Target**: monday.com Deals & Work Orders Boards | **Version**: 1.0.0

---

## 1. Executive Summary & Product Vision

Skylark Signal is a **founder decision cockpit** for monday.com sales and delivery operations. To prevent arithmetic hallucination, it enforces strict **separation of concerns**:
- **Deterministic Core**: 100% verified Python calculation of pipeline metrics, delivery bottlenecks, revenue at risk, and attention queue scores.
- **AI Phrasing Layer**: LLMs (OpenRouter/OpenAI) are used *exclusively* for natural language phrasing and response polishing.
- **Traceable Micro-Evidence**: Every metric and score is linked to canonical source record IDs and explicit formulas.

---

## 2. Key Technical & Data Assumptions

1. **Work Order Primary Key**: `Serial #` is canonical `work_order_id` (e.g., `SDPLDEAL-001`). `deal_reference` remains `None` unless source data proves 1-to-1 deal linkage.
2. **Account-Level Linkage**: Customer Code normalization links 175 of 176 Work Orders at customer account level (99.43% coverage) without fabricating fake record-level joins.
3. **Date & Text Canonicalization**: Dates parsed into ISO 8601 strings. Day-first dates (`05-04-2024` $\rightarrow$ `2024-04-05`) follow Indian business convention. Unparseable dates remain `None` with warning flags.
4. **Attention Queue Scoring Weight Rationale**: $\text{Score} = (0.40 \times \text{Financial}) + (0.30 \times \text{Urgency}) + (0.20 \times \text{Severity}) + (0.10 \times \text{Confidence})$.
   - *40% Financial*: Cash flow risk threatens runway. *30% Urgency*: Near-term due dates require unblocking. *20% Severity*: Status bottlenecks compound delay. *10% Confidence*: Penalizes missing fields.
5. **Mutually Exclusive Revenue at Risk**: Non-overlapping risk categories guarantee zero double-counting.
6. **Read-Only Local UI Affordances**: Recommended Actions checkboxes in the UI are local interactive presentation affordances for executive meetings and **never issue mutations/writes** to monday.com.

---

## 3. Key Architectural Trade-Offs & Rationale

| Decision | Chosen Approach | Alternative Considered | Rationale |
| :--- | :--- | :--- | :--- |
| **Engine** | Pure Python Deterministic Formulas | LLM Code Execution / Text-to-SQL | Eliminates metric hallucinations; provides 100% executive auditability. |
| **Ingestion** | Live GraphQL API + Offline JSON Fallback | Live API Only | Ensures 100% uptime even without active tokens or network access. |
| **LLM Strategy** | OpenRouter + OpenAI + Deterministic Fallback | Fixed Single Model (e.g. GPT-4o) | Gives founder model choice while ensuring full functionality with 0 API keys. |
| **Simulation** | Deep-Copy In-Memory Scenario Engine | Direct DB / Board State Mutation | Prevents hypothetical simulations from altering baseline board records. |

---

## 4. Interpretation of "Leadership Updates"

A **Leadership Update** is an executive-ready briefing for weekly founder syncs:
- **Business Health Badge**: Overall indicator (`GREEN`/`AMBER`/`RED`) derived from pipeline velocity and delivery bottlenecks.
- **Executive Pulse**: Direct 2-sentence narrative contrasting sales momentum against operational delivery delays.
- **Five Numbers to Quote**: Open Pipeline, Weighted Pipeline, Revenue at Risk, Active Work Orders, Data Trust Score.
- **Top Wins / Top Risks**: Categorized summary contrasting achievements with active threats.
- **Decisions Required**: Concrete action items specifying required leadership interventions.

---

## 5. Scope Triage & Conscious Trade-Offs (Sprint Retrospective)

1. **Account Linkage over Unverified Joins**: Implemented verified customer account matching rather than inventing speculative foreign keys.
2. **Poll-Based GraphQL over Webhooks**: Implemented 300s TTL-cached read-only GraphQL polling for simplicity and reliability.
3. **In-App Brief over External Push**: Built 1-click brief view with 4 export formats (`.md`, `.csv`, `.json`) keeping all capabilities self-contained.
