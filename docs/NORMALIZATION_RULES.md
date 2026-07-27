# Skylark Signal - Data Ingestion & Normalization Rules

**Document Version**: 1.1.0  
**Scope**: Source-Independent Ingestion & Data Normalization Architecture  
**Target Systems**: monday.com Deals Board & monday.com Work Orders Board  

---

## 1. Architectural Principles

1. **Source Independence**: The core normalizer (`src/skylark_signal/data/normalizer.py`) processes generic dictionary payloads. Excel loader adapters ingest local raw files, while future adapters can ingest monday.com GraphQL API payloads or webhook streams.
2. **Read-Only Raw File Integrity**: Raw source files (`data/raw/deals.xlsx` and `data/raw/work_orders.xlsx`) are treated as immutable. SHA256 checksums are calculated before and after processing to guarantee 0 file modifications.
3. **No Unsafe Imputation**: Missing probabilities, missing deal values, missing dates, owners, sectors, or stages are **never imputed or assigned default values**. Missing fields remain `None` and trigger structured quality flags.
4. **No Fabricated Exact Dates**: Text strings specifying quarters or financial periods (e.g., `"Q3 FY26"`) are preserved in `expected_close_period`. `expected_close_date` remains `None`, tagged with `period_without_exact_date`.
5. **No False Relational Links**: Work Orders `Serial #` (`SDPLDEAL-XXX`) is designated as `work_order_id`. `deal_reference` remains `None` because raw source sheets contain no verified row-level link to individual Deals records.

---

## 2. Source Cleaning & Ingestion Adapters

### Deals Ingestion (`load_deals_excel`)
- **Physical Worksheet Rows**: 347 (1 header row + 346 data rows).
- **Header Position**: Row index 0 (1-based Excel row 1).
- **Repeated Header Detection**: Filters 2 embedded header rows at indices 50 and 179 where `"Deal Stage" == "Deal Stage"`, `"Deal Status" == "Deal Status"`, or `"Sector/service" == "Sector/service"`.
- **Exact Duplicate Detection**: Identifies 12 exact duplicate business rows (identical string values across all 12 columns). Keeps one canonical copy in usable output and logs duplicate row indices in `data/processed/deals_rejected_or_duplicate_rows.csv`.
- **Usable Record Yield**: **332 canonical output rows** out of 347 physical worksheet rows.

### Work Orders Ingestion (`load_work_orders_excel`)
- **Physical Worksheet Rows**: 178.
- **Header Position**: Handles blank row index 0. Column titles are located at row index 1 (1-based Excel row 2). Data records start at row index 2 (1-based Excel row 3).
- **Blank Row Removal**: Filters 1 blank row (row index 0).
- **Usable Record Yield**: **176 canonical output rows** out of 178 physical worksheet rows.

---

## 3. Identifier Strategy

### Source Record ID (`source_record_id`)
A deterministic hash generated for every raw row:
```python
source_record_id = f"SRC-REC-{SHA256(file_hash + sheet_name + row_number)[:12]}"
```
Preserves exact traceability back to the raw source file position.

### Import Surrogate Key for Deals (`deal_id`)
Because the raw Deals dataset lacks an explicit primary key column, a deterministic surrogate import key is generated:
```python
deal_id = f"IMPORT-DEAL-{SHA256(file_hash + row_number + deal_name + customer)[:12]}"
```
*Note*: Documented explicitly as an import-time surrogate key, not a source-system identifier.

### Work Order Primary Key (`work_order_id`)
- Mapped directly from cleaned `Serial #` (e.g., `SDPLDEAL-075`).
- Validated for non-nullness and uniqueness across the dataset.
- `deal_reference` remains `None` (no fake deal links created).

---

## 4. Text & Category Normalization

### Customer Code Normalization (`normalize_customer_code`)
Harmonizes customer account codes across both boards into standard `COMPANY_XXX` format:
- `COMPANY005` → `COMPANY_005` (`customer_code_normalized`, `info`)
- `COMPANY_005` → `COMPANY_005` (`customer_code_normalized`, `info`)
- `WOCOMPANY_005` → `COMPANY_005` (`customer_code_normalized`, `info`)
- `WOCOMPANY_02` → `COMPANY_002` (`customer_code_fallback`, `info`)

*Quality Flags*:
- Standard & Fallback formats trigger `customer_code_normalized` or `customer_code_fallback` (`info` severity).
- Truly malformed codes trigger `malformed_customer_code` (`warning` severity).
- Missing codes trigger `missing_customer_code` (`error` severity).

### Category Taxonomy Mappings
Loaded dynamically from `config/`:
1. **Stage Mapping** (`config/stage_mapping.json`): Maps 16 raw stage values (e.g. `"A. Lead Generated"`, `"G. Project Won"`, `"L. Project Lost"`) to standard funnel stage names and sequential funnel order (1 to 12, 99 for Lost).
2. **Status Mapping** (`config/status_mapping.json`): Maps raw deal statuses (`Won`, `Dead`, `Open`, `On Hold`) and Work Order statuses (`Completed`, `Ongoing`, `Executed until current month`, etc.).
3. **Sector Mapping** (`config/sector_mapping.json`): Maps 11 industry sectors (`Mining`, `Renewables`, `Powerline`, `Railways`, `Construction`, etc.).

*Unmapped Categories*: Preserved as raw string values and tagged with `unknown_stage`, `unknown_status`, or `unknown_sector`.

---

## 5. Monetary & Percentage Parsing

### Money Parsing (`parse_money`)
- Strips currency symbols (`₹`, `$`, `Rs.`), commas, and spaces.
- Converts negative strings in parentheses `"(100.0)"` to `-100.0`.
- Text strings mixed with numbers extract numeric values and trigger `unparsed_money` warning.
- Missing values return `None` and trigger `missing_deal_value` flag.

### Percentage & Probability Parsing (`parse_probability`)
- Qualitative strings: `'High'` → 0.80, `'Medium'` → 0.50, `'Low'` → 0.20.
- Strings with `%` (e.g. `"100%"`, `"50%"`) → divided by 100 → `1.0`, `0.5`.
- Numeric values `0.0 <= val <= 1.0` → treated as decimal probability → `0.5`.
- Numeric values `1.0 < val <= 100.0` → divided by 100 → `0.5`.
- Values outside 0-100 → `None` plus `unparsed_probability` warning.
- **Never imputes missing probabilities** (247 usable nulls preserved).

---

## 6. Date Handling & Period Extraction

### Date Parsing (`parse_date`)
- Supports Excel `datetime` objects, ISO timestamps (`2025-06-30 00:00:00`), `DD/MM/YYYY`, `DD-MM-YYYY`, and month-name strings (`31 May 2025`).
- Returns ISO 8601 string `YYYY-MM-DD`.

### Ambiguous Date Protection
If a date like `"03/04/2025"` could be interpreted as DD/MM or MM/DD without explicit locale clues, the parsed date is stored with `is_ambiguous = True` and tagged with `ambiguous_date`.

### Quarter / Financial Period Extraction
Strings matching quarter or financial period regex (e.g., `"Q3 FY26"`, `"Q1 FY25"`):
- `expected_close_period` = `"Q3 FY26"`
- `expected_close_date` = `None`
- Quality flag = `period_without_exact_date`

---

## 7. Dynamic Tax Rate Validation

For Work Orders containing both exclusive (`excl`) and inclusive (`incl`) monetary values:
$$\text{implied\_tax\_rate} = \frac{\text{incl} - \text{excl}}{\text{excl}}$$

### Validation & Flags
- **Observed Dominant Rate**: `0.18` (18.00% GST) across 169 valid records.
- **Zero Exclusive Amount**: 6 records contain `excl = 0` where tax rate cannot be calculated.
- **Negative Rate / Incl < Excl**: Tagged with `unexpected_tax_rate` (severity: `error`).
- **High Rate (> 30%)**: Tagged with `unexpected_tax_rate` (severity: `warning`).

---

## 8. Quality Flag Taxonomy

| Quality Flag Code | Severity | Field | Description |
| :--- | :--- | :--- | :--- |
| `customer_code_normalized` | `info` | `customer` | Standard customer code format normalized to `COMPANY_XXX` |
| `customer_code_fallback` | `info` | `customer` | Customer code required zero-padding fallback normalization |
| `synthetic_deal_id` | `info` | `deal_id` | Assigned surrogate import key due to missing raw Deal ID |
| `no_source_deal_reference` | `info` | `deal_reference` | deal_reference remains null (no verified raw deal link) |
| `missing_deal_value` | `info` | `deal_value` | Deal value is missing in source row |
| `missing_probability` | `info` | `probability` | Win probability is missing in source row |
| `period_without_exact_date` | `info` | `expected_close_period` | Stored as period text without exact close date |
| `missing_exact_close_date` | `info` | `expected_close_date` | Tentative close date is missing |
| `ambiguous_date` | `warning` | Date fields | Date format day/month order is ambiguous |
| `unparsed_money` | `warning` | Money fields | Extracted numeric value from unparsed text |
| `unparsed_probability` | `warning` | `probability` | Probability text could not be parsed |
| `unknown_stage` | `warning` | `stage` | Raw stage value not found in taxonomy config |
| `unknown_status` | `warning` | `status` | Raw status value not found in taxonomy config |
| `unknown_sector` | `warning` | `sector` | Raw sector value not found in taxonomy config |
| `malformed_customer_code` | `warning` | `customer` | Customer code required regex fallback extraction |
| `unexpected_tax_rate` | `warning` / `error` | `implied_tax_rate` | Implied tax rate deviates from observed 18% GST |
| `missing_work_order_id` | `error` | `work_order_id` | Work Order Serial # is missing or invalid |
