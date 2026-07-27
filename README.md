# Skylark Signal - Founder Cockpit & Risk Intelligence Agent

**Skylark Signal** is a founder-facing business intelligence and risk intelligence system built for **monday.com Deals and Work Orders boards**.

---

## 🚀 Live Hosted Prototype & Evaluator Quickstart

The application can be deployed instantly to **Streamlit Community Cloud**, **Railway**, **Render**, or **Heroku**:
- **Hosted Startup Entrypoint**: [`app.py`](app.py)
- **Deployment Config**: [`.streamlit/config.toml`](.streamlit/config.toml) and [`Procfile`](Procfile)
- **Evaluation Readiness**: Launches cleanly without local setup; defaults to live monday.com API whenever credentials exist.

> 🔒 **Strict Read-Only Integration Guarantee**:
> All queries to monday.com use read-only GraphQL requests (`boards`, `items_page`). Recommended Action checkboxes displayed in the UI are local presentation affordances for executive task tracking during meetings and **NEVER** issue write actions or mutations back to monday.com.

---

## 🏗️ Architecture Overview

```text
                                  +---------------------------------------+
                                  |     Streamlit Founder Cockpit UI      |
                                  | (Ask | Investigate | Queue | Scenario)|
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Deterministic Analytics & Risk Engine|
                                  |  (Pipeline, Operations, Risk, Queue)  |
                                  +---------+-------------------+---------+
                                            |                   |
                                            v                   v
+-------------------------------+  +------------------+  +------------------+
|   Live monday.com GraphQL API |  | OpenRouter /     |  | Offline Processed|
| (Cursor Pagination & Cache)   |  | OpenAI LLM Client|  | JSON Files       |
+-------------------------------+  +------------------+  +------------------+
```

Skylark Signal strictly separates calculation logic from text generation:
- **Deterministic Analytics Engine**: 100% Python calculations for open pipeline, weighted pipeline, revenue at risk, and attention queue rankings.
- **AI Phrasing Layer**: Multi-provider LLM integration (OpenRouter / OpenAI) used exclusively for text phrasing in the Ask view.
- **Data Repository Layer**: Dual-mode repository that fetches live data from monday.com GraphQL API when credentials exist, or seamlessly uses processed clean snapshot files (`data/processed/`).

---

## ⚙️ Setup & Installation Instructions

### 1. Environment Configuration
Create a `.env` file in the root directory (refer to [`.env.example`](.env.example)):

```env
# monday.com API Credentials (Live monday API defaults when set)
MONDAY_API_TOKEN="your_personal_api_token_here"
MONDAY_DEALS_BOARD_ID="1234567890"
MONDAY_WORK_ORDERS_BOARD_ID="0987654321"

# OpenRouter & OpenAI Credentials (Optional - defaults to 100% deterministic mode if unset)
OPENROUTER_API_KEY="sk-or-v1-your_openrouter_api_key_here"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_API_KEY="sk-your_openai_api_key_here"
```

### 2. How to Run with Live monday.com Data
When `MONDAY_API_TOKEN`, `MONDAY_DEALS_BOARD_ID`, and `MONDAY_WORK_ORDERS_BOARD_ID` are configured in `.env`, Skylark Signal connects directly to monday.com via GraphQL with read-only cursor pagination and 300s TTL caching.

### 3. How Fallback Mode Works & When to Use It
- If `MONDAY_API_TOKEN` is unset or API connection fails, Skylark Signal operates in **Explicit Fallback Mode**, loading clean import snapshot records from `data/processed/deals_clean.json` and `data/processed/work_orders_clean.json`.
- The UI header will display a visible banner confirming `🟡 FALLBACK MODE ACTIVE`.

### 4. How to Run with & without LLM API Keys
- **Without API Keys (100% Offline / Deterministic Mode)**:
  Leave `OPENROUTER_API_KEY` and `OPENAI_API_KEY` unset. The app will launch normally, use deterministic routing, and format verified answer responses without calling remote LLM services.
- **With OpenRouter**:
  Set `OPENROUTER_API_KEY`. Launch the app and select your preferred model from the live OpenRouter model list picker in the sidebar.

---

## 🚀 Deployment Instructions (Streamlit Community Cloud)

1. Push this repository to GitHub.
2. Log into [share.streamlit.io](https://share.streamlit.io/).
3. Click **New App** and select this repository.
4. Set Main File Path to `app.py`.
5. Under **Advanced Settings $\rightarrow$ Secrets**, add your environment variables (`MONDAY_API_TOKEN`, `OPENROUTER_API_KEY`, etc.).
6. Click **Deploy!**

---

## 🧪 Running Automated Test Suite

```bash
# Run all 94+ unit and integration tests
pytest tests/ -v
```

---

## 📄 Deliverable Documentation

- **2-Page Architecture & Decision Log**: [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)
- **Data Quality Audit Report**: [`docs/DATA_AUDIT.md`](docs/DATA_AUDIT.md)
- **Normalization Pipeline Guide**: [`docs/NORMALIZATION_RULES.md`](docs/NORMALIZATION_RULES.md)
- **QA Verification Report**: [`docs/NORMALIZATION_QA_REPORT.md`](docs/NORMALIZATION_QA_REPORT.md)
- **monday.com Import Guide**: [`docs/MONDAY_IMPORT_GUIDE.md`](docs/MONDAY_IMPORT_GUIDE.md)
- **monday.com Read-Only API Spec**: [`docs/MONDAY_API_SPEC.md`](docs/MONDAY_API_SPEC.md)
- **Analytics Methodology Guide**: [`docs/ANALYTICS_METHODS.md`](docs/ANALYTICS_METHODS.md)
