# Skylark Signal - Founder Cockpit & Risk Intelligence Agent

**Skylark Signal** is a founder-facing business intelligence and risk intelligence system built for **monday.com Deals and Work Orders boards**.

🔗 **Live Demo:** https://skylark-signal.streamlit.app/
📁 **Repository:** (add your GitHub URL here)

---

## 🚀 Live Hosted Prototype & Evaluator Quickstart

The application is deployed on **Streamlit Community Cloud** and requires no local setup to evaluate:
- **Hosted Startup Entrypoint**: [`app.py`](app.py)
- **Deployment Config**: [`.streamlit/config.toml`](.streamlit/config.toml) and [`Procfile`](Procfile)
- **Evaluation Readiness**: Launches cleanly without local setup; defaults to live monday.com API whenever credentials exist, and falls back to a clearly labeled offline snapshot mode otherwise.

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

## 🖥️ Local Setup (Run It Yourself)

### 1. Clone and install

```bash
git clone <your-repo-url>
cd skylark-signal
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example file and fill in real values:

```bash
cp .env.example .env
```

See the **Environment Configuration** section below for what each variable does and how to obtain a monday.com API token.

### 3. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`. If no monday.com token is set, it will automatically launch in **Fallback Mode** using the bundled offline snapshot data — no credentials are required to try the app locally.

### 4. Run the test suite

```bash
pytest tests/ -v
```

---

## ⚙️ Environment Configuration

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

### How to get a monday.com API token

1. Log into monday.com.
2. Click your profile avatar → **Developers** (or **Admin → API** depending on your plan).
3. Under **My Access Tokens**, click **Show** or **Generate** to get your personal API (v2) token.
4. Copy it into `MONDAY_API_TOKEN` — treat it like a password; never commit it to git.

### How to get your board IDs

Open each board (Deals, Work Orders) in your browser. The numeric ID in the URL —
`https://yourteam.monday.com/boards/1234567890` — is the board ID. Use these for
`MONDAY_DEALS_BOARD_ID` and `MONDAY_WORK_ORDERS_BOARD_ID`.

---

## How Each Mode Works

### Live monday.com Mode
When `MONDAY_API_TOKEN`, `MONDAY_DEALS_BOARD_ID`, and `MONDAY_WORK_ORDERS_BOARD_ID` are configured, Skylark Signal connects directly to monday.com via GraphQL with read-only cursor pagination and 300s TTL caching. The sidebar displays 🟢 **LIVE MONDAY API**.

### Fallback Mode
If `MONDAY_API_TOKEN` is unset or the API connection fails, Skylark Signal operates in **Explicit Fallback Mode**, loading clean import snapshot records from `data/processed/deals_clean.json` and `data/processed/work_orders_clean.json`. The UI displays a visible 🟡 **FALLBACK MODE ACTIVE** banner explaining why.

### LLM Phrasing Modes
- **Without API keys (100% Offline / Deterministic Mode)**: Leave `OPENROUTER_API_KEY` and `OPENAI_API_KEY` unset. The app launches normally, uses deterministic routing, and formats verified answers without calling any remote LLM service.
- **With OpenRouter**: Set `OPENROUTER_API_KEY`. Launch the app and select your preferred model from the live OpenRouter model list picker in the sidebar.
- **With OpenAI**: Set `OPENAI_API_KEY` and select the OpenAI provider in the sidebar.

In all cases, LLMs are used exclusively for phrasing — no metric or calculation is ever produced by a model.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Log into [share.streamlit.io](https://share.streamlit.io/).
3. Click **New App** and select this repository.
4. Set **Main File Path** to `app.py`.
5. Under **Advanced Settings → Secrets**, add your environment variables in TOML format:
   ```toml
   MONDAY_API_TOKEN = "your_personal_api_token_here"
   MONDAY_DEALS_BOARD_ID = "1234567890"
   MONDAY_WORK_ORDERS_BOARD_ID = "0987654321"
   OPENROUTER_API_KEY = "sk-or-v1-your_openrouter_api_key_here"
   ```
6. Click **Deploy!** Streamlit will generate a public URL that serves the live app to any evaluator with no local setup required.

---

## 🧪 Running the Automated Test Suite

```bash
pytest tests/ -v
```

Covers data normalization, monday.com API client behavior (mocked), analytics metrics, revenue-at-risk logic, scenario simulation, LLM client routing/fallback, clarification engine, and UI session state.

---

## 📄 Deliverable Documentation

- **Architecture & Decision Log**: [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)
- **Data Quality Audit Report**: [`docs/DATA_AUDIT.md`](docs/DATA_AUDIT.md)
- **Normalization Pipeline Guide**: [`docs/NORMALIZATION_RULES.md`](docs/NORMALIZATION_RULES.md)
- **QA Verification Report**: [`docs/NORMALIZATION_QA_REPORT.md`](docs/NORMALIZATION_QA_REPORT.md)
- **monday.com Import Guide**: [`docs/MONDAY_IMPORT_GUIDE.md`](docs/MONDAY_IMPORT_GUIDE.md)
- **monday.com Read-Only API Spec**: [`docs/MONDAY_API_SPEC.md`](docs/MONDAY_API_SPEC.md)
- **Analytics Methodology Guide**: [`docs/ANALYTICS_METHODS.md`](docs/ANALYTICS_METHODS.md)

> **Before submitting:** confirm each linked doc above actually exists in your repo and isn't an empty file — broken links here are worse than not listing them.
