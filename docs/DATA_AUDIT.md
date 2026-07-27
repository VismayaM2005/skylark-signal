# Skylark Signal - Data Audit Report

**Technical Assignment**: Skylark Signal - Founder-Facing BI Agent  
**Audit Scope**: monday.com Deals (`data/raw/deals.xlsx`) and Work Orders (`data/raw/work_orders.xlsx`) Raw Datasets  
**Audit Date**: July 27, 2026  

---

## 1. Executive Summary

This document presents a rigorous, comprehensive data audit of the **Deals** and **Work Orders** raw datasets for **Skylark Signal**. The goal of this audit is to establish raw dataset integrity, profile every worksheet and column, identify data-quality defects, recommend canonical schemas and monday.com board structures, evaluate cross-board entity matching mechanisms, and delineate feasible business intelligence analytics.

**Crucial Findings Summary**:
- **Dataset Scale**: Raw Deals contains **346 rows** (332 usable business records after filtering 2 repeated header rows and 12 exact duplicate business rows). Raw Work Orders contains **178 rows** (176 usable business records after removing 1 blank header row).
- **Primary Key Deficit**: The raw Deals dataset lacks an explicit `deal_id` or `Serial #` primary key column. The Work Orders dataset contains a `Serial #` column (formatted as `SDPLDEAL-XXX`), but these cannot be mapped directly to Deals rows due to the absence of corresponding identifiers in the Deals sheet.
- **Customer-Level vs Deal-Level Matching**: Normalizing customer codes (`WOCOMPANY_XXX` in Work Orders and `COMPANYXXX` in Deals to standard `COMPANY_XXX`) links **175 out of 176 Work Orders (99.43%)** to customer accounts present in the Deals dataset across **50 shared customer accounts**. However, **this represents account-level linkage, not individual Deal-to-Work-Order record matching**.
- **Masked Alias Discrepancy**: Generic Deal Name aliases (e.g., `"Sakura"`, `"Scooby-Doo"`) were generated independently across the two boards during masking, rendering `(Deal Name + Customer)` matching ineffective (matching only 1 of 176 Work Orders).
- **Data Integrity**: Both raw Excel files were audited without modification. SHA256 checksums verified 100% data preservation.

---

## 2. Dataset Overview

### Raw File Verification & Checksums

| Dataset | Raw File Path | Sheet Name | SHA256 Checksum (Before & After) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Deals** | `data/raw/deals.xlsx` | `Deal tracker` | `a40f462176202ed09cd046d5ed9c70eae855e7811de7b85ca4704b27b75e2174` | Verified Untouched |
| **Work Orders** | `data/raw/work_orders.xlsx` | `work order tracker` | `4459274f93936757f644cd1acae37b17bace818063cbaa576b9af8dd89085105` | Verified Untouched |

### Detailed Row Count Breakdown

| Metric | Deals Dataset (`Deal tracker`) | Work Orders Dataset (`work order tracker`) |
| :--- | :--- | :--- |
| **Raw Worksheet Rows** | 346 | 178 |
| **Raw Worksheet Columns** | 12 | 38 |
| **Blank Rows Removed** | 0 | 1 (Row index 0) |
| **Header Rows Offset** | Row index 0 | Row index 1 (Column titles) |
| **Repeated Embedded Header Rows** | 2 (Row indices 50 & 179) | 0 |
| **Exact Duplicate Business Rows** | 12 | 0 |
| **Final Usable Business Records** | **332** | **176** |

---

## 3. Deals Findings

### Sheet Metrics & Column Profiles
- **Worksheet Name**: `Deal tracker`
- **Total Usable Records**: 332
- **Column Count**: 12

| Source Column | Inferred Dtype | Missing Count | Missing % | Unique Values | Sample Values | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Deal Name` | `string` | 0 | 0.0% | 155 | `"Naruto"`, `"Sasuke"`, `"Sakura"` | Masked Deal Title (Anime Codenames) |
| `Owner code` | `string` | 15 | 4.52% | 8 | `"OWNER_003"`, `"OWNER_001"`, `"OWNER_002"` | Sales Rep / Account Manager ID |
| `Client Code` | `string` | 0 | 0.0% | 199 | `"COMPANY005"`, `"COMPANY038"`, `"COMPANY133"` | Customer Account ID (`COMPANYXXX`) |
| `Deal Status` | `string` | 1 | 0.30% | 4 | `"Won"`, `"Dead"`, `"Open"`, `"On Hold"` | High-Level Sales Outcome |
| `Close Date (A)` | `string` / `date` | 304 | 91.57% | 20 | `"2025-06-30 00:00:00"`, `"31/05/2025"` | Actual Close Date |
| `Closure Probability`| `string` / `float`| 249 | 75.0% | 11 | `"100%"`, `"50%"`, `"0.5"` | Expected Close Probability |
| `Masked Deal value` | `float` | 173 | 52.11% | 134 | `500000.0`, `1250000.0` | Masked Deal Monetary Value |
| `Tentative Close Date`| `string` / `date` | 70 | 21.08% | 125 | `"2025-08-31 00:00:00"`, `"Q3 FY26"` | Expected Close Date |
| `Deal Stage` | `string` | 0 | 0.0% | 16 | `"A. Lead Generated"`, `"G. Project Won"` | Pipeline Funnel Stage |
| `Product deal` | `string` | 166 | 50.0% | 10 | `"Pure Service"`, `"Service + Spectra"` | Deliverable Product / Service Type |
| `Sector/service` | `string` | 8 | 2.41% | 11 | `"Mining"`, `"Powerline"`, `"Renewables"` | Industry Sector |
| `Created Date` | `string` / `date` | 1 | 0.30% | 215 | `"2025-04-01 00:00:00"` | Deal Creation Timestamp |

### Key Quality Issues in Deals
1. **Repeated Header Rows**: Embedded header rows at index 50 and 179 contain literal string column names (`"Sector/service"`, `"Created Date"`, `"Deal Stage"`) as data values.
2. **Missing Deal Primary Key**: No `deal_id` column exists. `Deal Name` is non-unique (`"Sakura"` appears 16 times across different client codes).
3. **High Null Rate in Key Metrics**: `Close Date (A)` is missing in 91.57% of rows; `Closure Probability` is missing in 75.0%; `Masked Deal value` is missing in 52.11%.
4. **Mixed Date & Probability Formats**: Dates contain ISO timestamps (`"2025-06-30 00:00:00"`), slash formats (`"31/05/2025"`), and quarter descriptions (`"Q3 FY26"`). Probability contains strings (`"100%"`), decimals (`"0.5"`), and empty strings.

---

## 4. Work Orders Findings

### Sheet Metrics & Column Profiles
- **Worksheet Name**: `work order tracker`
- **Total Usable Records**: 176
- **Column Count**: 38

| Key Source Column | Inferred Dtype | Missing Count | Missing % | Unique Values | Sample Values | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Deal name masked` | `string` | 0 | 0.0% | 58 | `"Scooby-Doo"`, `"Appa"`, `"Sakura"` | Work Order Project Name |
| `Customer Name Code` | `string` | 0 | 0.0% | 51 | `"WOCOMPANY_002"`, `"WOCOMPANY_038"` | Customer Account ID (`WOCOMPANY_XXX`) |
| `Serial #` | `string` | 0 | 0.0% | 176 | `"SDPLDEAL-075"`, `"SDPLDEAL-101"` | Work Order Identifier / PO Reference |
| `Nature of Work` | `string` | 12 | 6.82% | 4 | `"One time Project"`, `"Monthly Contract"` | Contract / Engagement Nature |
| `Execution Status` | `string` | 4 | 2.27% | 7 | `"Completed"`, `"Ongoing"`, `"Not Started"` | Field Execution Status |
| `Probable Start Date` | `date` | 19 | 10.8% | 105 | `2025-05-31` | Scheduled Execution Start Date |
| `Probable End Date` | `date` | 11 | 6.25% | 112 | `2025-06-03` | Scheduled Execution End Date |
| `BD/KAM Personnel code`| `string` | 11 | 6.25% | 7 | `"OWNER_003"`, `"OWNER_001"` | Account Representative ID |
| `Sector` | `string` | 0 | 0.0% | 6 | `"Mining"`, `"Powerline"`, `"Renewables"` | Industry Sector |
| `Amount Excl GST` | `float` | 1 | 0.57% | 165 | `264398.08`, `154150.0` | Contract Amount (Excl. Tax) |
| `Amount Incl GST` | `float` | 0 | 0.0% | 167 | `311989.7344`, `181897.0` | Contract Amount (Incl. Tax) |
| `Invoice Status` | `string` | 64 | 36.36% | 6 | `"Fully Billed"`, `"Partially Billed"` | Financial Billing Status |
| `WO Status (billed)` | `string` | 74 | 42.05% | 2 | `"Open"`, `"Closed"` | Work Order Financial Closure |

### Completely Empty / Unreliable Columns in Work Orders
- `Expected Billing Month`: **176 / 176 Missing (100.0%)** - Completely unpopulated column.
- `Actual Collection Month`: **176 / 176 Missing (100.0%)** - Completely unpopulated column.
- `Collection status`: **176 / 176 Missing (100.0%)** - Completely unpopulated column.
- `Collection Date`: **176 / 176 Missing (100.0%)** - Completely unpopulated column.
- `AR Priority account`: **166 / 176 Missing (94.32%)** - Sparse priority flag.

---

## 5. Data-Quality Risks

1. **Missing Primary Key in Deals**: No `deal_id` column exists in `deals.xlsx`. Generating synthetic identifiers is required for pipeline tracking.
2. **Anonymization Mismatch Across Boards**: `Customer Name Code` uses `WOCOMPANY_XXX` while `Client Code` uses `COMPANYXXX`. Normalizing via regex `COMPANY_\d{3}` solves customer-level matching, but `Deal Name` masks (`"Sakura"`, `"Scooby-Doo"`) were generated independently across sheets.
3. **Sparse Financial & Date Fields**: Over 52% of deal values and 91% of deal close dates are missing in Deals, impairing pipeline forecasting.
4. **Duplicate Business Records**: 12 exact duplicate rows in Deals inflate raw pipeline volume if uncleaned.

---

## 6. Cross-Board Matching Analysis

### Entity Level Distinction
- **Customer-Level Matching**: Identifies which customer account (`COMPANY_XXX`) owns Deals and Work Orders.
- **Deal-Level Matching**: Connects a specific Work Order to the exact Deal opportunity that created it.
- **Work-Order-Level Matching**: Identifies individual work orders (`SDPLDEAL-XXX`).

### Customer-Level Matching Breakdown
- **Unique Normalized Customers in Deals**: 199 (`COMPANY_001` - `COMPANY_200`)
- **Unique Normalized Customers in Work Orders**: 51 (`COMPANY_001` - `COMPANY_051`)
- **Shared Customers (Appearing in Both)**: 50 customers
- **Work Orders Linked to Deals Customer Account**: **175 out of 176 Work Orders (99.43%)** (Only `WOCOMPANY_017` / `COMPANY_017` has 1 Work Order and 0 Deals).

#### Cardinality Breakdown of the 50 Matched Customers
| Cardinality Category | Definition | Matched Customer Count | % of Matched Customers | Business Implications |
| :--- | :--- | :--- | :--- | :--- |
| **1-to-1** | 1 Deal, 1 Work Order | **17 customers** | 34.0% | Exact customer-level association maps to a single Deal & Work Order. |
| **1-to-Many** | 1 Deal, M Work Orders | **26 customers** | 52.0% | Single deal generated multiple execution work orders (e.g. rate contracts). |
| **Many-to-1** | N Deals, 1 Work Order | **4 customers** | 8.0% | Multiple deal opportunities exist for a customer with 1 active work order. |
| **Many-to-Many** | N Deals, M Work Orders | **3 customers** | 6.0% | Complex account relationships with multiple deals and work orders. |

### Evaluation of Proposed Join Methods

| Join Method | Join Fields Used | Classification | Expected Match Count | Failure / False Match Risks |
| :--- | :--- | :--- | :--- | :--- |
| **Method 1: Direct Deal ID** | `deal_id` (Deals) = `Serial #` (WO) | **Unsafe** | 0 / 176 (0%) | Deals dataset lacks a `deal_id` / `Serial #` column. |
| **Method 2: Normalized Customer Code** | `norm_customer` (`COMPANY_XXX`) | **Strong (Customer-Level)** | 175 / 176 (99.43%) | Links records to customer account, but **cannot resolve specific deal** when customer has multiple deals (74% of records). |
| **Method 3: Masked Deal Name + Customer** | `Deal Name` + `norm_customer` | **Weak / Unsafe** | 1 / 176 (0.57%) | Anonymization masks (`"Sakura"`, `"Scooby-Doo"`) were assigned independently in each file. |
| **Method 4: Customer + Sector + Value** | `norm_customer` + `Sector` + `Value` | **Unsafe** | 0 / 176 (0%) | Deal values and WO contract amounts do not match due to masking or GST/tax scope differences. |
| **Method 5: Compound Fuzzy Matching** | Fuzzy `(Customer, Sector, Owner, Date)` | **Moderate (Heuristic)** | ~40-60 Estimated | Risk of false positive linkages when accounts have multiple concurrent deals in the same sector. |

---

## 7. Recommended Canonical Schemas

### Canonical Deals Schema (`config/deals_schema.json`)
- `deal_id`: Synthetic primary key (`string`, required) - Generated via UUID/Hash.
- `deal_name`: Deal title (`string`, required) - Raw: `Deal Name`.
- `customer`: Customer code (`string`, required) - Normalized from `Client Code` to `COMPANY_XXX`.
- `sector`: Industry sector (`string`, optional) - Mapped to canonical sector taxonomy.
- `stage`: Funnel stage (`string`, required) - Mapped to canonical stage taxonomy (`Lead Generated` to `Project Won`).
- `deal_value`: Monetary value (`float`, optional) - Cast from `Masked Deal value`.
- `probability`: Win probability (`float`, optional) - Parsed from `Closure Probability` (0.0 - 1.0).
- `expected_close_date`: Target close date (`date`, optional) - ISO 8601 string.
- `actual_close_date`: Actual close date (`date`, optional) - Raw: `Close Date (A)`.
- `owner`: Account manager (`string`, optional) - Raw: `Owner code`.
- `created_date`: Creation date (`date`, required) - Raw: `Created Date`.
- `status`: High-level deal status (`string`, required) - `Won`, `Dead`, `Open`, `On Hold`.

### Canonical Work Orders Schema (`config/work_orders_schema.json`)
- `work_order_id`: Work order identifier (`string`, required) - Raw: `Serial #` (`SDPLDEAL-XXX`).
- `work_order_name`: Work order title (`string`, required) - Raw: `Deal name masked`.
- `deal_reference`: Reference deal ID (`string`, optional) - Raw: `Serial #`.
- `customer`: Customer code (`string`, required) - Normalized from `Customer Name Code` (`WOCOMPANY_XXX` -> `COMPANY_XXX`).
- `sector`: Industry sector (`string`, optional) - Raw: `Sector`.
- `nature_of_work`: Engagement type (`string`, optional) - Raw: `Nature of Work`.
- `project_value_excl_gst`: Amount excl. tax (`float`, optional) - Raw: `Amount in Rupees (Excl of GST) (Masked)`.
- `project_value_incl_gst`: Amount incl. tax (`float`, optional) - Raw: `Amount in Rupees (Incl of GST) (Masked)`.
- `start_date`: Execution start date (`date`, optional) - Raw: `Probable Start Date`.
- `due_date`: Execution end date (`date`, optional) - Raw: `Probable End Date`.
- `completion_date`: Data delivery date (`date`, optional) - Raw: `Data Delivery Date`.
- `status`: Execution status (`string`, required) - Raw: `Execution Status` (`Completed`, `Ongoing`, etc.).
- `owner`: BD/KAM Personnel (`string`, optional) - Raw: `BD/KAM Personnel code`.

---

## 8. Recommended monday.com Board Structures

### Board 1: monday.com Deals Board
- **Item Name**: `deal_name` (Name Column)
- **Customer Code**: `customer` (Text Column)
- **Sector**: `sector` (Status / Color Column)
- **Sales Stage**: `stage` (Status / Color Column)
- **Deal Status**: `status` (Status / Color Column)
- **Deal Value**: `deal_value` (Numbers Column - Currency INR)
- **Win Probability**: `probability` (Numbers Column - Percentage)
- **Tentative Close Date**: `expected_close_date` (Date Column)
- **Actual Close Date**: `actual_close_date` (Date Column)
- **Deal Owner**: `owner` (People / Text Column)
- **Created Date**: `created_date` (Date Column)

### Board 2: monday.com Work Orders Board
- **Item Name**: `work_order_name` (Name Column)
- **Work Order ID**: `work_order_id` (Text Column)
- **Customer Code**: `customer` (Text Column)
- **Sector**: `sector` (Status / Color Column)
- **Execution Status**: `status` (Status / Color Column)
- **Contract Value (Excl GST)**: `project_value_excl_gst` (Numbers Column)
- **Contract Value (Incl GST)**: `project_value_incl_gst` (Numbers Column)
- **Probable Start Date**: `start_date` (Date Column)
- **Probable End Date**: `due_date` (Date Column)
- **Data Delivery Date**: `completion_date` (Date Column)
- **Invoice Status**: `invoice_status` (Status / Color Column)
- **BD/KAM Owner**: `owner` (People / Text Column)

---

## 9. Analytics Currently Possible

1. **Deals Funnel & Stage Conversion**: Total deals count by stage, stage distribution, win vs loss rates.
2. **Customer Account Revenue & Volume**: Total deals and work orders per customer account (`COMPANY_XXX`).
3. **Sector Breakdown**: Portfolio distribution across Mining, Renewables, Powerline, Railways, and Construction.
4. **Owner Sales Performance**: Deal volume and work order distribution by account manager (`OWNER_001`, `OWNER_003`).
5. **Work Order Execution Tracking**: Completion rate, ongoing vs completed projects count.

---

## 10. Analytics Currently Unreliable or Impossible

1. **Direct Deal-to-Work-Order Conversion Rate**: Impossible at 100% precision due to missing `deal_id` in Deals dataset.
2. **Deal Velocity & Time-in-Stage**: Unreliable due to 91.57% missing `Close Date (A)` and missing stage transition logs.
3. **Payment Collection Aging & AR Analysis**: Impossible due to 100% missing values in `Collection Date`, `Collection status`, `Actual Collection Month`, and `Expected Billing Month`.
4. **Pipeline Revenue Forecasting**: Highly uncertain due to 52.11% missing deal values and 75.0% missing probability ratings.

---

## 11. Assumptions Requiring Validation

1. **Customer Anonymization Mapping**: Assumed `WOCOMPANY_002` maps exactly to `COMPANY002` / `COMPANY_002`.
2. **Work Order Serial Formatting**: Assumed `Serial #` (`SDPLDEAL-XXX`) represents work order numbers rather than raw deal keys.
3. **Multi-Year Scope**: Assumed dates spanning 2025 and 2026 reflect actual operational quarters.
4. **GST Tax Structure**: Assumed 18% standard GST delta between Excl and Incl tax values.

---

## 12. Ten Most Important Findings

1. **Missing Primary Key in Deals**: Raw Deals lacks a `deal_id` column, blocking direct 1-to-1 relational joins.
2. **99.43% Customer-Level Match Rate**: Normalizing customer codes links 175 of 176 Work Orders to customer accounts in Deals across 50 matched accounts.
3. **Account-Level vs Deal-Level Distinction**: Shared customer codes prove account ownership, but do not prove which specific Deal generated a Work Order when customers have multiple deals.
4. **Independent Anonymization Masks**: Deal Name aliases (`"Sakura"`, `"Scooby-Doo"`) were generated independently across sheets, breaking `(Deal Name + Customer)` joins.
5. **Repeated Header Rows in Deals**: Embedded header rows at index 50 and 179 contain column names as string values.
6. **Work Orders Header Offset**: Work Orders contains an empty row 0 and header title row at row index 1.
7. **100% Missing Payment Collection Fields**: Four financial collection columns in Work Orders are completely empty.
8. **12 Exact Duplicate Rows in Deals**: Uncleaned Deals raw data contains 12 duplicate business rows.
9. **Sparse Pipeline Financials**: 52.11% of deal values and 75.0% of win probabilities are missing in Deals.
10. **Raw File Preservation Verified**: SHA256 hashes confirm both raw Excel files remained 100% untouched.

---

## 13. Recommended Next Engineering Step

**Recommended Action**: Implement an automated Data Ingestion & Normalization Pipeline (`src/ingestion/`) that:
1. Cleans raw Excel files (stripping header offsets and embedded header rows).
2. Normalizes customer codes to canonical `COMPANY_XXX` format.
3. Assigns deterministic synthetic primary keys to Deals records.
4. Exports standardized clean CSV/Parquet tables ready for monday.com synchronization and BI dashboard rendering.
