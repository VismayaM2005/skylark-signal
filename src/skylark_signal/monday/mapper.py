import re, json
from typing import List, Dict, Any, Optional, Tuple
from skylark_signal.monday.schemas import (
    MondayBoard,
    MondayColumn,
    MondayItem,
    ColumnMappingResult,
    SchemaMappingReport
)
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.data.quality import QualityFlag, create_quality_flag
from skylark_signal.data.identifiers import generate_source_record_id, generate_synthetic_deal_id
from skylark_signal.utils.text import clean_text, normalize_customer_code, map_category
from skylark_signal.utils.money import parse_money, calculate_implied_tax_rate
from skylark_signal.utils.percentages import parse_probability
from skylark_signal.utils.dates import parse_date

DEALS_CANONICAL_ALIASES = {
    "deal_name": ["deal name", "name", "item name", "deal title", "opportunity"],
    "customer": ["customer code", "client code", "customer", "client", "company code", "company"],
    "sector": ["sector", "sector/service", "industry", "domain"],
    "stage": ["deal stage", "stage", "sales stage", "funnel stage"],
    "status": ["deal status", "status", "outcome"],
    "deal_value": ["deal value", "masked deal value", "value", "amount", "deal amount"],
    "probability": ["win probability", "closure probability", "probability", "win %"],
    "expected_close_date": ["tentative close date", "expected close date", "close date"],
    "expected_close_period": ["tentative close period", "close period", "quarter"],
    "actual_close_date": ["actual close date", "close date (a)", "won date"],
    "owner": ["deal owner", "owner code", "owner", "account manager", "kam"],
    "created_date": ["created date", "creation date", "date created"],
    "product_or_service": ["product or service", "product deal", "product", "service"]
}

WO_CANONICAL_ALIASES = {
    "work_order_id": ["work order id", "serial #", "serial number", "wo id", "po number"],
    "work_order_name": ["work order name", "deal name masked", "name", "project name"],
    "customer": ["customer code", "customer name code", "customer", "client"],
    "sector": ["sector", "industry"],
    "nature_of_work": ["nature of work", "engagement type", "work type"],
    "execution_status": ["execution status", "status", "wo status"],
    "project_value_excl_tax": ["contract value excl tax", "amount in rupees (excl of gst) (masked)", "amount excl gst", "value excl tax"],
    "project_value_incl_tax": ["contract value incl tax", "amount in rupees (incl of gst) (masked)", "amount incl gst", "value incl tax"],
    "start_date": ["probable start date", "start date", "commencement date"],
    "due_date": ["probable end date", "due date", "completion target"],
    "completion_date": ["completion date", "data delivery date", "delivery date"],
    "invoice_status": ["invoice status"],
    "billing_status": ["billing status"],
    "owner": ["owner", "bd/kam personnel code", "bd owner", "kam"]
}

def clean_title(title: str) -> str:
    """Normalizes string for fuzzy title matching."""
    return re.sub(r'[^a-z0-9]', '', title.lower())

class BoardSchemaMapper:
    """Dynamic schema mapper for translating monday.com boards into canonical records."""

    def __init__(
        self,
        stage_mapping_path: str = "config/stage_mapping.json",
        status_mapping_path: str = "config/status_mapping.json",
        sector_mapping_path: str = "config/sector_mapping.json"
    ):
        with open(stage_mapping_path, 'r') as f:
            self.stage_config = json.load(f).get("deals_stage_taxonomy", {})
            
        with open(status_mapping_path, 'r') as f:
            st_cfg = json.load(f)
            self.deals_status_cfg = st_cfg.get("deals_status", {})
            self.wo_exec_cfg = st_cfg.get("work_orders_execution_status", {})
            self.wo_inv_cfg = st_cfg.get("work_orders_invoice_status", {})
            self.wo_bill_cfg = st_cfg.get("work_orders_billing_status", {})
            
        with open(sector_mapping_path, 'r') as f:
            self.sector_config = json.load(f).get("raw_to_canonical_sector", {})

    def inspect_and_map_schema(
        self,
        board: MondayBoard,
        is_deals_board: bool = True
    ) -> Tuple[SchemaMappingReport, Dict[str, MondayColumn]]:
        """
        Inspects board columns dynamically and produces a SchemaMappingReport and field-to-column map.
        """
        aliases_dict = DEALS_CANONICAL_ALIASES if is_deals_board else WO_CANONICAL_ALIASES
        
        mapped_results: List[ColumnMappingResult] = []
        field_to_column: Dict[str, MondayColumn] = {}
        mapped_col_ids = set()

        for c_field, aliases in aliases_dict.items():
            best_col: Optional[MondayColumn] = None
            best_score = 0.0
            best_rule = "unmapped"

            for col in board.columns:
                col_title_clean = clean_title(col.title)
                c_field_clean = clean_title(c_field)

                # 1. Exact title match
                if col_title_clean == c_field_clean:
                    best_col = col
                    best_score = 1.0
                    best_rule = "exact_title_match"
                    break
                
                # 2. Alias match
                for alias in aliases:
                    alias_clean = clean_title(alias)
                    if col_title_clean == alias_clean:
                        if best_score < 0.95:
                            best_col = col
                            best_score = 0.95
                            best_rule = "alias_exact_match"
                    elif alias_clean in col_title_clean or col_title_clean in alias_clean:
                        if best_score < 0.85:
                            best_col = col
                            best_score = 0.85
                            best_rule = "alias_partial_match"

            if best_col and best_score >= 0.70:
                field_to_column[c_field] = best_col
                mapped_col_ids.add(best_col.id)
                mapped_results.append(ColumnMappingResult(
                    canonical_field=c_field,
                    monday_column_id=best_col.id,
                    monday_column_title=best_col.title,
                    monday_column_type=best_col.type,
                    confidence_score=best_score,
                    mapping_rule=best_rule
                ))
            else:
                mapped_results.append(ColumnMappingResult(
                    canonical_field=c_field,
                    monday_column_id=None,
                    monday_column_title=None,
                    monday_column_type=None,
                    confidence_score=0.0,
                    mapping_rule="unresolved"
                ))

        unresolved_canonical = [r.canonical_field for r in mapped_results if r.confidence_score < 0.70]
        unmapped_monday = [c.title for c in board.columns if c.id not in mapped_col_ids]
        
        scores = [r.confidence_score for r in mapped_results]
        overall_conf = round(sum(scores) / len(scores), 4) if scores else 0.0

        report = SchemaMappingReport(
            board_id=board.id,
            board_name=board.name,
            mapped_columns=mapped_results,
            unresolved_canonical_fields=unresolved_canonical,
            unmapped_monday_columns=unmapped_monday,
            overall_confidence=overall_conf
        )

        return report, field_to_column

    def map_monday_deal_item(
        self,
        item: MondayItem,
        board: MondayBoard,
        field_to_col: Dict[str, MondayColumn]
    ) -> CanonicalDealRecord:
        """Maps a single MondayItem from a Deals board into a CanonicalDealRecord."""
        raw_vals: Dict[str, Any] = {"Name": item.name}
        col_val_map = {cv.id: cv for cv in item.column_values}

        for c_field, col in field_to_col.items():
            if col.id in col_val_map:
                cv = col_val_map[col.id]
                raw_vals[col.title] = cv.text or cv.value or ""

        flags: List[QualityFlag] = []
        exclusion_reasons: List[str] = []

        # 1. Identifiers
        deal_name = clean_text(item.name) or f"Deal Item {item.id}"
        
        raw_client = raw_vals.get(field_to_col.get("customer", MondayColumn(id="", title="", type="")).title)
        customer, cust_flag_code, cust_sev, cust_warn = normalize_customer_code(raw_client)
        flags.append(create_quality_flag(
            code=cust_flag_code,
            severity=cust_sev,
            message=cust_warn or f"Customer code normalized as '{customer}'",
            field="customer",
            raw_value=raw_client
        ))
        customer = customer or "COMPANY_UNKNOWN"

        source_rec_id = generate_source_record_id("MONDAY_API", board.name, int(item.id) if item.id.isdigit() else 0)
        deal_id = generate_synthetic_deal_id("MONDAY_API", int(item.id) if item.id.isdigit() else 0, deal_name, customer)

        flags.append(create_quality_flag(
            code="synthetic_deal_id",
            severity="info",
            message=f"Assigned import surrogate key {deal_id} for Monday item {item.id}",
            field="deal_id"
        ))

        # 2. Sector
        raw_sector = raw_vals.get(field_to_col.get("sector", MondayColumn(id="", title="", type="")).title)
        sector, _, _ = map_category(raw_sector, self.sector_config)

        # 3. Stage & Status
        raw_stage = raw_vals.get(field_to_col.get("stage", MondayColumn(id="", title="", type="")).title)
        stage, _, _ = map_category(raw_stage, self.stage_config)
        stage = stage or "Unmapped Stage"

        raw_status = raw_vals.get(field_to_col.get("status", MondayColumn(id="", title="", type="")).title)
        status, _, _ = map_category(raw_status, self.deals_status_cfg)
        status = status or "Open"

        # 4. Money & Probability
        raw_val = raw_vals.get(field_to_col.get("deal_value", MondayColumn(id="", title="", type="")).title)
        deal_val, _, _, val_warn = parse_money(raw_val)
        if deal_val is None:
            flags.append(create_quality_flag(code="missing_deal_value", severity="info", message="Deal value missing", field="deal_value", affects_metrics=True))
            exclusion_reasons.append("missing_deal_value")

        raw_prob = raw_vals.get(field_to_col.get("probability", MondayColumn(id="", title="", type="")).title)
        prob, _, _, _ = parse_probability(raw_prob)
        if prob is None:
            flags.append(create_quality_flag(code="missing_probability", severity="info", message="Win probability missing", field="probability", affects_metrics=True))
            exclusion_reasons.append("missing_probability")

        # 5. Dates
        raw_tent = raw_vals.get(field_to_col.get("expected_close_date", MondayColumn(id="", title="", type="")).title)
        exp_date, exp_period, exp_stat, exp_amb, _ = parse_date(raw_tent)

        raw_act = raw_vals.get(field_to_col.get("actual_close_date", MondayColumn(id="", title="", type="")).title)
        act_date, _, _, _, _ = parse_date(raw_act)

        raw_crt = raw_vals.get(field_to_col.get("created_date", MondayColumn(id="", title="", type="")).title)
        crt_date, _, _, _, _ = parse_date(raw_crt) or item.created_at

        owner = clean_text(raw_vals.get(field_to_col.get("owner", MondayColumn(id="", title="", type="")).title))
        prod = clean_text(raw_vals.get(field_to_col.get("product_or_service", MondayColumn(id="", title="", type="")).title))

        return CanonicalDealRecord(
            source_system="monday.com API",
            source_file=f"monday_board_{board.id}",
            source_sheet=board.name,
            source_row_number=int(item.id) if item.id.isdigit() else 0,
            source_record_id=source_rec_id,
            deal_id=deal_id,
            deal_name=deal_name,
            customer=customer,
            sector=sector,
            stage=stage,
            status=status,
            deal_value=deal_val,
            probability=prob,
            expected_close_date=exp_date,
            expected_close_period=exp_period,
            actual_close_date=act_date,
            owner=owner,
            created_date=crt_date,
            product_or_service=prod,
            raw_values=raw_vals,
            quality_flags=flags,
            excluded_from_metrics=len(exclusion_reasons) > 0,
            exclusion_reasons=exclusion_reasons
        )

    def map_monday_work_order_item(
        self,
        item: MondayItem,
        board: MondayBoard,
        field_to_col: Dict[str, MondayColumn]
    ) -> CanonicalWorkOrderRecord:
        """Maps a single MondayItem from a Work Orders board into a CanonicalWorkOrderRecord."""
        raw_vals: Dict[str, Any] = {"Name": item.name}
        col_val_map = {cv.id: cv for cv in item.column_values}

        for c_field, col in field_to_col.items():
            if col.id in col_val_map:
                cv = col_val_map[col.id]
                raw_vals[col.title] = cv.text or cv.value or ""

        flags: List[QualityFlag] = []
        exclusion_reasons: List[str] = []

        # 1. Work Order ID
        raw_wo_id = clean_text(raw_vals.get(field_to_col.get("work_order_id", MondayColumn(id="", title="", type="")).title))
        wo_id = raw_wo_id if raw_wo_id else f"WO-ITEM-{item.id}"

        # 2. Customer
        raw_cust = raw_vals.get(field_to_col.get("customer", MondayColumn(id="", title="", type="")).title)
        customer, cust_flag_code, cust_sev, cust_warn = normalize_customer_code(raw_cust)
        flags.append(create_quality_flag(
            code=cust_flag_code,
            severity=cust_sev,
            message=cust_warn or f"Customer code normalized as '{customer}'",
            field="customer",
            raw_value=raw_cust
        ))
        customer = customer or "COMPANY_UNKNOWN"

        source_rec_id = generate_source_record_id("MONDAY_API", board.name, int(item.id) if item.id.isdigit() else 0)

        # 3. Deal Reference (MUST REMAIN NONE)
        flags.append(create_quality_flag(code="no_source_deal_reference", severity="info", message="deal_reference remains null", field="deal_reference"))

        # 4. Sector & Nature
        raw_sector = raw_vals.get(field_to_col.get("sector", MondayColumn(id="", title="", type="")).title)
        sector, _, _ = map_category(raw_sector, self.sector_config)
        nature = clean_text(raw_vals.get(field_to_col.get("nature_of_work", MondayColumn(id="", title="", type="")).title))

        # 5. Financials & Tax
        raw_excl = raw_vals.get(field_to_col.get("project_value_excl_tax", MondayColumn(id="", title="", type="")).title)
        excl_val, _, _, _ = parse_money(raw_excl)
        raw_incl = raw_vals.get(field_to_col.get("project_value_incl_tax", MondayColumn(id="", title="", type="")).title)
        incl_val, _, _, _ = parse_money(raw_incl)

        tax_rate, tax_sev, tax_msg = calculate_implied_tax_rate(excl_val, incl_val)

        # 6. Dates & Statuses
        raw_start = raw_vals.get(field_to_col.get("start_date", MondayColumn(id="", title="", type="")).title)
        start_date, _, _, _, _ = parse_date(raw_start)
        raw_due = raw_vals.get(field_to_col.get("due_date", MondayColumn(id="", title="", type="")).title)
        due_date, _, _, _, _ = parse_date(raw_due)
        raw_comp = raw_vals.get(field_to_col.get("completion_date", MondayColumn(id="", title="", type="")).title)
        comp_date, _, _, _, _ = parse_date(raw_comp)

        raw_exec = raw_vals.get(field_to_col.get("execution_status", MondayColumn(id="", title="", type="")).title)
        exec_status, _, _ = map_category(raw_exec, self.wo_exec_cfg)
        exec_status = exec_status or "Not Started"

        raw_inv = raw_vals.get(field_to_col.get("invoice_status", MondayColumn(id="", title="", type="")).title)
        inv_status, _, _ = map_category(raw_inv, self.wo_inv_cfg)

        raw_bill = raw_vals.get(field_to_col.get("billing_status", MondayColumn(id="", title="", type="")).title)
        bill_status, _, _ = map_category(raw_bill, self.wo_bill_cfg)

        owner = clean_text(raw_vals.get(field_to_col.get("owner", MondayColumn(id="", title="", type="")).title))

        return CanonicalWorkOrderRecord(
            source_system="monday.com API",
            source_file=f"monday_board_{board.id}",
            source_sheet=board.name,
            source_row_number=int(item.id) if item.id.isdigit() else 0,
            source_record_id=source_rec_id,
            work_order_id=wo_id,
            work_order_name=item.name,
            deal_reference=None,
            customer=customer,
            sector=sector,
            nature_of_work=nature,
            project_value_excl_tax=excl_val,
            project_value_incl_tax=incl_val,
            implied_tax_rate=tax_rate,
            start_date=start_date,
            due_date=due_date,
            completion_date=comp_date,
            execution_status=exec_status,
            invoice_status=inv_status,
            billing_status=bill_status,
            progress=None,
            owner=owner,
            location=None,
            raw_values=raw_vals,
            quality_flags=flags,
            excluded_from_metrics=len(exclusion_reasons) > 0,
            exclusion_reasons=exclusion_reasons
        )
