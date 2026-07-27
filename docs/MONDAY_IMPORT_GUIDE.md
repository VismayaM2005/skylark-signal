# Skylark Signal - monday.com Board Setup & CSV Import Guide

**Document Version**: 1.0.0  
**Target Systems**: monday.com Workspace Boards  
**Import Files Location**: `data/processed/deals_clean.csv` and `data/processed/work_orders_clean.csv`  

---

## 1. Overview & Import Prerequisites

This guide provides step-by-step instructions for manual CSV import of cleaned **Deals** and **Work Orders** data into monday.com.

### Source Files to Import
1. **Deals Board CSV**: `data/processed/deals_clean.csv` (**332 records**)
2. **Work Orders Board CSV**: `data/processed/work_orders_clean.csv` (**176 records**)

---

## 2. monday.com Deals Board Creation

### Step 1: Create New Board
1. In monday.com, click **+ Add** → **New Board**.
2. Board Name: `Skylark Signal - Deals`.
3. Select **Board Privacy**: Main / Private.
4. Select **What are you managing in this board?**: *Deals / Items*.

### Step 2: Configure Column Structure & Types

| Imported CSV Column Name | Item / Column Title | Recommended monday.com Column Type | Mapping Notes |
| :--- | :--- | :--- | :--- |
| `Deal Name` | **Item Name** | **Name Column** | **Primary Item Title** |
| `Import Deal ID` | Import Deal ID | Text Column | Surrogate import key (`IMPORT-DEAL-XXX`) |
| `Customer Code` | Customer Code | Text Column | Standardized `COMPANY_XXX` |
| `Sector` | Sector | Status Column | Colored dropdown labels |
| `Deal Stage` | Deal Stage | Status Column | Colored funnel stage labels |
| `Deal Status` | Deal Status | Status Column | `Won`, `Dead`, `Open`, `On Hold` |
| `Deal Value` | Deal Value | Numbers Column | Set format to Currency (INR / ₹) |
| `Win Probability` | Win Probability | Numbers Column | Set format to Percentage (%) |
| `Tentative Close Date` | Tentative Close Date | Date Column | Target close date YYYY-MM-DD |
| `Tentative Close Period`| Tentative Close Period| Text Column | Period text e.g. `Q3 FY26` |
| `Actual Close Date` | Actual Close Date | Date Column | Actual close date YYYY-MM-DD |
| `Deal Owner` | Deal Owner | People / Text Column | Account manager code |
| `Created Date` | Created Date | Date Column | Deal creation date |
| `Product or Service` | Product or Service | Dropdown Column | Deliverable product type |
| `Data Quality Severity` | Quality Severity | Status Column | `clean`, `info`, `warning`, `error` |
| `Data Quality Issues` | Quality Issues | Text Column | Data quality flag log |
| `Source Row Number` | Source Row | Numbers Column | Raw Excel source row reference |

---

## 3. monday.com Work Orders Board Creation

### Step 1: Create New Board
1. In monday.com, click **+ Add** → **New Board**.
2. Board Name: `Skylark Signal - Work Orders`.
3. Select **Board Privacy**: Main / Private.
4. Select **What are you managing in this board?**: *Projects / Work Orders*.

### Step 2: Configure Column Structure & Types

| Imported CSV Column Name | Item / Column Title | Recommended monday.com Column Type | Mapping Notes |
| :--- | :--- | :--- | :--- |
| `Work Order Name` | **Item Name** | **Name Column** | **Primary Item Title** |
| `Work Order ID` | Work Order ID | Text Column | Canonical `SDPLDEAL-XXX` |
| `Customer Code` | Customer Code | Text Column | Standardized `COMPANY_XXX` |
| `Sector` | Sector | Status Column | Colored dropdown labels |
| `Nature of Work` | Nature of Work | Dropdown Column | Engagement type |
| `Execution Status` | Execution Status | Status Column | `Completed`, `Ongoing`, etc. |
| `Contract Value Excl Tax`| Value (Excl Tax) | Numbers Column | Currency (INR / ₹) |
| `Contract Value Incl Tax`| Value (Incl Tax) | Numbers Column | Currency (INR / ₹) |
| `Implied Tax Rate` | Implied Tax Rate | Numbers Column | Percentage (%) |
| `Probable Start Date` | Probable Start Date | Date Column | Execution start date |
| `Probable End Date` | Probable End Date | Date Column | Execution end date |
| `Completion Date` | Completion Date | Date Column | Data delivery date |
| `Invoice Status` | Invoice Status | Status Column | Billing status |
| `Billing Status` | Billing Status | Status Column | Billed / Stuck |
| `Owner` | BD / KAM Owner | People / Text Column | Representative code |
| `Data Quality Severity` | Quality Severity | Status Column | `clean`, `info`, `warning`, `error` |
| `Data Quality Issues` | Quality Issues | Text Column | Data quality flag log |
| `Source Row Number` | Source Row | Numbers Column | Raw Excel source row reference |

> [!IMPORTANT]
> **Why `deal_reference` / `Deal Reference (Unavailable)` is blank**:  
> Raw Work Orders sheet `Serial #` (`SDPLDEAL-XXX`) represents the Work Order ID itself. The raw Deals sheet contains no matching `Serial #` or `deal_id` column. Creating a fake deal link would introduce false relationships into monday.com. `Deal Reference (Unavailable)` remains blank until an explicit deal lookup is verified.

---

## 4. Step-by-Step CSV Import Procedure

1. Open the target monday.com board (`Skylark Signal - Deals` or `Skylark Signal - Work Orders`).
2. Click the board menu **(...)** at the top right → **Import Data** → **Excel / CSV**.
3. Drag and drop the corresponding clean CSV file (`deals_clean.csv` or `work_orders_clean.csv`).
4. **Column Mapping Step**:
   - Map `Deal Name` (Deals) or `Work Order Name` (Work Orders) as the **Item Name** column.
   - Match all other CSV columns to their designated monday.com column types per the tables above.
5. **Date Formatting Settings**:
   - Ensure date columns use standard ISO format `YYYY-MM-DD` to prevent monday.com from auto-converting dates based on browser locale.
6. **Import Execution**: Click **Start Import**.

---

## 5. Post-Import Verification & Board Registration

### Verification Checklist
- [ ] Confirm **Deals Board** contains exactly **332 items**.
- [ ] Confirm **Work Orders Board** contains exactly **176 items**.
- [ ] Confirm `Quality Severity` status colors render correctly (`info` = blue, `warning` = orange, `error` = red).
- [ ] Confirm no numbers or percentages were corrupted during import.

### Record Board IDs
After creating and importing the boards, note down the monday.com Board IDs from the browser URL (`https://yourcompany.monday.com/boards/<BOARD_ID>`):

```env
MONDAY_DEALS_BOARD_ID=<your_deals_board_id>
MONDAY_WORK_ORDERS_BOARD_ID=<your_work_orders_board_id>
```
Store these Board IDs in `.env` for future GraphQL API synchronization.
