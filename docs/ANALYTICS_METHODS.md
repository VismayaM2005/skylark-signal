# Skylark Signal - Deterministic Analytics & Risk Engine Methodology

**Document Version**: 1.0.0  
**Scope**: Deterministic Business Intelligence, Revenue at Risk Modeling, Founder Attention Queue, Data Trust Scoring  

---

## 1. Executive Overview

**Skylark Signal** implements a **100% deterministic Python analytics engine**. No LLM is used to compute numbers or risk scores. All metrics, risk buckets, attention queue rankings, data trust scores, and evidence bundles are calculated using pure, explainable Python code.

---

## 2. Sales Pipeline & Funnel Metrics (`pipeline_metrics.py`)

### 2.1 Funnel Status Definitions
- **Open Deals**: Deals where status is `"Open"` or stage is not `"G. Project Won"`, `"L. Project Lost"`, `"Won"`, `"Lost"`, `"Dead"`.
- **Won Deals**: Deals where status is `"Won"` / `"Closed Won"` or stage is `"G. Project Won"`.
- **Lost Deals**: Deals where status is `"Lost"` / `"Closed Lost"` / `"Dead"` or stage is `"L. Project Lost"`.

### 2.2 Financial Formulas
- **Total Open Pipeline**: Sum of `deal_value` across all open deals:
  $$\text{Total Open Pipeline} = \sum_{d \in \text{OpenDeals}} \text{deal\_value}_d$$
- **Weighted Open Pipeline**: Sum of probability-weighted deal values:
  $$\text{Weighted Pipeline} = \sum_{d \in \text{OpenDeals}} (\text{deal\_value}_d \times \text{probability}_d)$$
- **Win Rate**: Ratio of won deals to closed deals:
  $$\text{Win Rate} = \frac{|\text{WonDeals}|}{|\text{WonDeals}| + |\text{LostDeals}|}$$
- **Customer Concentration (Top 3)**:
  $$\text{Top 3 Concentration} = \frac{\sum_{i=1}^3 \text{Pipeline}_{\text{Customer}_i}}{\text{Total Open Pipeline}} \times 100\%$$

---

## 3. Operations & Delivery Metrics (`operations_metrics.py`)

### 3.1 Work Order Status Definitions
- **Active Work Orders**: Work Orders with status `"Ongoing"`, `"Not Started"`, `"Pending"`, `"Executed until current month"`, `"Blocked"`, `"Delayed"`, `"On Hold"`.
- **Completed Work Orders**: Work Orders with status `"Completed"`, `"Executed"`, `"Closed"`.
- **Overdue Work Orders**: Active Work Orders where `due_date` or `completion_date` $<$ Reference Date (`2026-07-27`).

---

## 4. Cross-Board Account Linkage & Match Hierarchy (`cross_board_metrics.py`)

### 4.1 Match Level Taxonomy
1. **`shared_customer_match`** (Primary Bridge): Standardized customer code matching (`COMPANY_XXX`). Links 175 out of 176 Work Orders across 50 shared customer accounts.
2. **`confirmed_record_match`**: Direct row-level link between a specific Deal ID and Work Order ID. (Set to **0** because raw source sheets contain no verified row-level deal references).
3. **`unmatched`**: Work Orders or Deals belonging to single-board customer accounts.

---

## 5. Non-Overlapping Revenue-at-Risk Engine (`risk.py`)

To prevent double-counting, every dollar of revenue at risk is assigned to **exactly ONE mutually exclusive category**:

| Risk Category | Inclusions & Rule Criteria | Exclusions (Double-Counting Prevention) | Confidence |
| :--- | :--- | :--- | :--- |
| **`blocked_or_delayed_active_work_orders`** | Active Work Orders with status `Blocked`, `Delayed`, or `On Hold`. | N/A (Highest priority operational risk) | 0.95 |
| **`overdue_active_work_orders`** | Active Work Orders past target completion date. | Excludes Work Orders already counted in Category 1 | 0.90 |
| **`stale_late_stage_deals`** | Open Deals in Stage $\ge$ "Proposal Sent" past close date or missing close date. | Excludes Closed Won/Lost deals | 0.85 |
| **`high_value_missing_probability_deals`** | Open Deals $\ge$ 75th percentile value missing closure probability rating. | Excludes Deals already counted in Category 3 | 0.80 |

---

## 6. Founder Attention Queue Multi-Dimensional Scoring (`attention_queue.py`)

Items in the Founder Attention Queue are ranked dynamically by a weighted multi-dimensional score:

$$\text{Total Score} = (S_{\text{Financial}} \times 0.40) + (S_{\text{Urgency}} \times 0.30) + (S_{\text{Severity}} \times 0.20) + (S_{\text{Confidence}} \times 0.10)$$

### Priority Classification
- **`P1-Critical`**: Total Score $\ge 80.0$
- **`P2-High`**: Total Score $65.0 - 79.9$
- **`P3-Medium`**: Total Score $< 65.0$

---

## 7. Data Trust Score Methodology (`data_trust.py`)

The **Data Trust Score (0-100)** evaluates overall data reliability across 5 components:

1. **Deals Value & Probability Completeness** (35%)
2. **Work Orders Primary Key & Value Completeness** (30%)
3. **Date Validity & Non-Ambiguity** (20%)
4. **Category Mapping Success Rate** (10%)
5. **Shared Customer Coverage Ratio** (5%)
