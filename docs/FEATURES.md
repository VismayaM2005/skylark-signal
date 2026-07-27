# Skylark Signal — Features Reference (Verified)

This file lists only features that were actually implemented and validated in the project.

## 1) Data quality and normalization

- Deterministic record identifiers for source rows and canonical outputs
- Repeatable output generation with SHA256 hash verification
- Raw-file integrity checks to confirm source Excel files were not modified
- Import-ready CSV and JSON outputs for monday.com boards
- Structured data-quality flags for missing, malformed, ambiguous, or unknown values
- Customer-code normalization across Deals and Work Orders
- Date parsing with explicit handling of ambiguous and quarter-style values
- Money and percentage parsing with validation and failure reporting

## 2) Monday.com integration

- Read-only monday.com GraphQL integration
- Dynamic board schema inspection
- Cursor-based pagination
- Canonical mapping of live monday fields to internal record models
- Unresolved-column reporting when source columns do not map cleanly
- Board snapshot repository for live or fallback data loading

## 3) Analytics

- Deterministic pipeline metrics
- Deterministic operations metrics
- Cross-board customer-level matching
- Revenue-at-risk analysis with non-overlapping buckets
- Founder Attention Queue
- Data Trust Score
- Evidence generation for metrics and recommendations

## 4) Scenario and decision support

- Scenario Simulator with no mutation of baseline data
- Baseline vs. scenario-adjusted comparisons
- Delta reporting for affected metrics
- Copy-ready leadership brief generation
- Executive pulse, top risks, recommended actions, and key numbers to quote

## 5) Conversational experience

- Ask view for founder-level questions
- Clarifying questions when the query is ambiguous
- Multi-turn conversational context
- Deterministic fallback when no model is available
- OpenRouter model selection from a live model list
- Provider/status visibility for selected model and fallback mode

## 6) UI and product presentation

- Investigate view with filters, charts, and evidence drill-down
- Brief view with board-ready leadership formatting
- System status indicators for data source, trust score, and provider state
- Downloadable exports for the leadership brief and supporting evidence

## 7) Tests and validation

- Automated tests for normalization, monday integration, analytics, and UI state
- Repeatability checks across multiple runs
- Validation that no fake Deal Reference is created
- Validation that no missing probabilities are imputed
- Validation that quarter text is not converted into fabricated exact dates

## 8) Submission artifacts

- `README.md`
- `docs/DECISION_LOG.md`
- `docs/ANALYTICS_METHODS.md`
- `docs/NORMALIZATION_RULES.md`
- `docs/MONDAY_IMPORT_GUIDE.md`
- `data/processed/` exports for import and reference
- Streamlit-ready application entry point

## Notes

- The project is designed so that all numeric business outputs come from deterministic Python logic.
- LLM usage is restricted to phrasing, intent interpretation, and optional text polishing.
- Live monday.com data is the primary source path when credentials and board IDs are available.
- Fallback data exists only as an explicit resilience mode.
