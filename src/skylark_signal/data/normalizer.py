import json
from typing import Dict, Any, Tuple, Optional, List
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.data.quality import QualityFlag, create_quality_flag
from skylark_signal.data.identifiers import (
    generate_source_record_id,
    generate_synthetic_deal_id,
    validate_work_order_id
)
from skylark_signal.utils.text import clean_text, normalize_customer_code, map_category
from skylark_signal.utils.money import parse_money, calculate_implied_tax_rate
from skylark_signal.utils.percentages import parse_probability
from skylark_signal.utils.dates import parse_date

def load_json_config(filepath: str) -> Dict[str, Any]:
    """Loads a JSON configuration file."""
    with open(filepath, 'r') as f:
        return json.load(f)

class RecordNormalizer:
    """
    Source-independent normalizer for Deals and Work Orders records.
    Can process dict inputs from Excel adapters, monday.com API payloads, or JSON streams.
    """
    def __init__(
        self,
        stage_mapping_path: str = "config/stage_mapping.json",
        status_mapping_path: str = "config/status_mapping.json",
        sector_mapping_path: str = "config/sector_mapping.json"
    ):
        self.stage_config = load_json_config(stage_mapping_path).get("deals_stage_taxonomy", {})
        
        status_cfg = load_json_config(status_mapping_path)
        self.deals_status_config = status_cfg.get("deals_status", {})
        self.wo_execution_status_config = status_cfg.get("work_orders_execution_status", {})
        self.wo_invoice_status_config = status_cfg.get("work_orders_invoice_status", {})
        self.wo_billing_status_config = status_cfg.get("work_orders_billing_status", {})
        
        self.sector_config = load_json_config(sector_mapping_path).get("raw_to_canonical_sector", {})

    def normalize_deal(self, row_info: Dict[str, Any]) -> CanonicalDealRecord:
        """Normalizes a raw Deals row dict into a CanonicalDealRecord."""
        raw = row_info.get("raw_values", {})
        file_hash = row_info.get("file_hash", "UNKNOWN")
        source_file = row_info.get("source_file", "deals.xlsx")
        source_sheet = row_info.get("source_sheet", "Deal tracker")
        row_num = row_info.get("source_row_number", 0)
        
        flags: List[QualityFlag] = []
        exclusion_reasons: List[str] = []
        
        # 1. Source Identifiers
        source_rec_id = generate_source_record_id(file_hash, source_sheet, row_num)
        raw_deal_name = clean_text(raw.get("Deal Name"))
        deal_name = raw_deal_name if raw_deal_name else f"Deal Row {row_num}"
        
        if not raw_deal_name:
            flags.append(create_quality_flag(
                code="missing_deal_name",
                severity="warning",
                message="Deal Name is missing in raw row",
                field="deal_name",
                raw_value=raw.get("Deal Name"),
                recommended_action="Assign descriptive deal name"
            ))

        # 2. Customer Normalization
        raw_client = raw.get("Client Code")
        customer, cust_flag_code, cust_severity, cust_warn = normalize_customer_code(raw_client)
        flags.append(create_quality_flag(
            code=cust_flag_code, # 'customer_code_normalized', 'customer_code_fallback', 'malformed_customer_code', 'missing_customer_code'
            severity=cust_severity, # 'info', 'warning', or 'error'
            message=cust_warn or f"Customer code normalized as '{customer}'",
            field="customer",
            raw_value=raw_client,
            recommended_action="Standardize customer code format" if cust_severity in ("warning", "error") else None
        ))
        customer = customer or "COMPANY_UNKNOWN"

        # 3. Synthetic Import Deal ID
        deal_id = generate_synthetic_deal_id(file_hash, row_num, deal_name, customer)
        flags.append(create_quality_flag(
            code="synthetic_deal_id",
            severity="info",
            message=f"Assigned surrogate import key {deal_id} due to missing source primary key",
            field="deal_id",
            recommended_action="Maintain surrogate key for import tracking"
        ))

        # 4. Sector
        raw_sector = raw.get("Sector/service")
        sector, sec_mapped, _ = map_category(raw_sector, self.sector_config)
        if not sec_mapped and raw_sector is not None:
            flags.append(create_quality_flag(
                code="unknown_sector",
                severity="warning",
                message=f"Unknown sector '{raw_sector}' preserved",
                field="sector",
                raw_value=raw_sector,
                recommended_action="Update config/sector_mapping.json taxonomy"
            ))

        # 5. Stage & Status
        raw_stage = raw.get("Deal Stage")
        stage, stage_mapped, _ = map_category(raw_stage, self.stage_config)
        if not stage_mapped and raw_stage is not None:
            flags.append(create_quality_flag(
                code="unknown_stage",
                severity="warning",
                message=f"Unknown deal stage '{raw_stage}' preserved",
                field="stage",
                raw_value=raw_stage,
                recommended_action="Update config/stage_mapping.json taxonomy"
            ))
        stage = stage or "Unmapped Stage"

        raw_status = raw.get("Deal Status")
        status, status_mapped, _ = map_category(raw_status, self.deals_status_config)
        if not status_mapped and raw_status is not None:
            flags.append(create_quality_flag(
                code="unknown_status",
                severity="warning",
                message=f"Unknown deal status '{raw_status}' preserved",
                field="status",
                raw_value=raw_status,
                recommended_action="Update config/status_mapping.json taxonomy"
            ))
        status = status or "Open"

        # 6. Money / Deal Value
        raw_value = raw.get("Masked Deal value")
        deal_val, val_ok, _, val_warn = parse_money(raw_value)
        if deal_val is None:
            flags.append(create_quality_flag(
                code="missing_deal_value",
                severity="info",
                message="Deal value is missing",
                field="deal_value",
                raw_value=raw_value,
                affects_metrics=True,
                recommended_action="Provide estimated deal value"
            ))
            exclusion_reasons.append("missing_deal_value")
        elif not val_ok:
            flags.append(create_quality_flag(
                code="unparsed_money",
                severity="warning",
                message=val_warn or "Failed to parse monetary value",
                field="deal_value",
                raw_value=raw_value
            ))

        # 7. Probability
        raw_prob = raw.get("Closure Probability")
        prob, prob_ok, _, prob_warn = parse_probability(raw_prob)
        if prob is None:
            flags.append(create_quality_flag(
                code="missing_probability",
                severity="info",
                message="Closure probability is missing (not imputed)",
                field="probability",
                raw_value=raw_prob,
                affects_metrics=True,
                recommended_action="Provide win probability"
            ))
            exclusion_reasons.append("missing_probability")
        elif not prob_ok:
            flags.append(create_quality_flag(
                code="unparsed_probability",
                severity="warning",
                message=prob_warn or "Invalid probability format",
                field="probability",
                raw_value=raw_prob
            ))

        # 8. Dates
        raw_tent_date = raw.get("Tentative Close Date")
        exp_date, exp_period, exp_stat, exp_amb, exp_fail = parse_date(raw_tent_date)
        if exp_stat == 'parsed_period':
            flags.append(create_quality_flag(
                code="period_without_exact_date",
                severity="info",
                message=exp_fail or f"Stored period '{exp_period}' without exact close date",
                field="expected_close_period",
                raw_value=raw_tent_date
            ))
        elif exp_amb:
            flags.append(create_quality_flag(
                code="ambiguous_date",
                severity="warning",
                message=exp_fail or "Ambiguous date format",
                field="expected_close_date",
                raw_value=raw_tent_date
            ))
        elif exp_date is None and exp_period is None:
            flags.append(create_quality_flag(
                code="missing_exact_close_date",
                severity="info",
                message="Tentative close date is missing",
                field="expected_close_date",
                raw_value=raw_tent_date
            ))

        raw_close_date = raw.get("Close Date (A)")
        act_date, _, act_stat, act_amb, _ = parse_date(raw_close_date)
        if act_amb:
            flags.append(create_quality_flag(
                code="ambiguous_date",
                severity="warning",
                message="Ambiguous actual close date format",
                field="actual_close_date",
                raw_value=raw_close_date
            ))

        raw_created_date = raw.get("Created Date")
        created_date, _, _, crt_amb, _ = parse_date(raw_created_date)
        if crt_amb:
            flags.append(create_quality_flag(
                code="ambiguous_date",
                severity="warning",
                message="Ambiguous created date format",
                field="created_date",
                raw_value=raw_created_date
            ))

        owner = clean_text(raw.get("Owner code"))
        product_deal = clean_text(raw.get("Product deal"))

        return CanonicalDealRecord(
            source_system="Excel",
            source_file=source_file,
            source_sheet=source_sheet,
            source_row_number=row_num,
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
            created_date=created_date,
            product_or_service=product_deal,
            raw_values={k: str(v) for k, v in raw.items()},
            quality_flags=flags,
            excluded_from_metrics=len(exclusion_reasons) > 0,
            exclusion_reasons=exclusion_reasons
        )

    def normalize_work_order(self, row_info: Dict[str, Any]) -> CanonicalWorkOrderRecord:
        """Normalizes a raw Work Orders row dict into a CanonicalWorkOrderRecord."""
        raw = row_info.get("raw_values", {})
        file_hash = row_info.get("file_hash", "UNKNOWN")
        source_file = row_info.get("source_file", "work_orders.xlsx")
        source_sheet = row_info.get("source_sheet", "work order tracker")
        row_num = row_info.get("source_row_number", 0)
        
        flags: List[QualityFlag] = []
        exclusion_reasons: List[str] = []
        
        source_rec_id = generate_source_record_id(file_hash, source_sheet, row_num)
        
        # 1. Work Order ID (Serial #)
        raw_serial = clean_text(raw.get("Serial #"))
        wo_id_valid, wo_id_warn = validate_work_order_id(raw_serial)
        work_order_id = raw_serial if raw_serial else f"WO-ROW-{row_num}"
        if not wo_id_valid:
            flags.append(create_quality_flag(
                code="missing_work_order_id",
                severity="error",
                message=wo_id_warn or "Work Order ID issue",
                field="work_order_id",
                raw_value=raw.get("Serial #"),
                affects_metrics=True,
                recommended_action="Assign valid Work Order Serial #"
            ))
            exclusion_reasons.append("missing_work_order_id")

        # 2. Work Order Name
        raw_name = clean_text(raw.get("Deal name masked"))
        wo_name = raw_name if raw_name else f"Work Order {work_order_id}"

        # 3. Deal Reference (MUST REMAIN NONE)
        deal_reference = None
        flags.append(create_quality_flag(
            code="no_source_deal_reference",
            severity="info",
            message="deal_reference remains null (no verified deal lookup in raw file)",
            field="deal_reference"
        ))

        # 4. Customer Normalization
        raw_cust = raw.get("Customer Name Code")
        customer, cust_flag_code, cust_severity, cust_warn = normalize_customer_code(raw_cust)
        flags.append(create_quality_flag(
            code=cust_flag_code, # 'customer_code_normalized', 'customer_code_fallback', 'malformed_customer_code', 'missing_customer_code'
            severity=cust_severity,
            message=cust_warn or f"Customer code normalized as '{customer}'",
            field="customer",
            raw_value=raw_cust
        ))
        customer = customer or "COMPANY_UNKNOWN"

        # 5. Sector
        raw_sector = raw.get("Sector")
        sector, _, _ = map_category(raw_sector, self.sector_config)

        nature_of_work = clean_text(raw.get("Nature of Work"))

        # 6. Financial Values & Tax Calculation
        raw_excl = raw.get("Amount in Rupees (Excl of GST) (Masked)")
        excl_val, excl_ok, _, excl_warn = parse_money(raw_excl)
        if not excl_ok:
            flags.append(create_quality_flag(
                code="unparsed_money",
                severity="warning",
                message=excl_warn or "Failed to parse exclusive contract value",
                field="project_value_excl_tax",
                raw_value=raw_excl
            ))

        raw_incl = raw.get("Amount in Rupees (Incl of GST) (Masked)")
        incl_val, incl_ok, _, incl_warn = parse_money(raw_incl)
        if not incl_ok:
            flags.append(create_quality_flag(
                code="unparsed_money",
                severity="warning",
                message=incl_warn or "Failed to parse inclusive contract value",
                field="project_value_incl_tax",
                raw_value=raw_incl
            ))

        tax_rate, tax_severity, tax_warn = calculate_implied_tax_rate(excl_val, incl_val)
        if tax_warn and tax_severity:
            flags.append(create_quality_flag(
                code="unexpected_tax_rate",
                severity=tax_severity, # "info", "warning", or "error"
                message=tax_warn,
                field="implied_tax_rate",
                raw_value=f"excl:{excl_val}, incl:{incl_val}",
                recommended_action="Verify tax calculation and contract tax terms"
            ))

        # 7. Dates
        raw_start = raw.get("Probable Start Date")
        start_date, _, _, st_amb, _ = parse_date(raw_start)
        if st_amb:
            flags.append(create_quality_flag(
                code="ambiguous_date",
                severity="warning",
                message="Ambiguous start date format",
                field="start_date",
                raw_value=raw_start
            ))

        raw_due = raw.get("Probable End Date")
        due_date, _, _, due_amb, _ = parse_date(raw_due)
        if due_amb:
            flags.append(create_quality_flag(
                code="ambiguous_date",
                severity="warning",
                message="Ambiguous end date format",
                field="due_date",
                raw_value=raw_due
            ))

        raw_comp = raw.get("Data Delivery Date")
        comp_date, _, _, comp_amb, _ = parse_date(raw_comp)
        if comp_amb:
            flags.append(create_quality_flag(
                code="ambiguous_date",
                severity="warning",
                message="Ambiguous data delivery date format",
                field="completion_date",
                raw_value=raw_comp
            ))

        # 8. Status Mappings
        raw_exec = raw.get("Execution Status")
        exec_status, exec_mapped, _ = map_category(raw_exec, self.wo_execution_status_config)
        if not exec_mapped and raw_exec is not None:
            flags.append(create_quality_flag(
                code="unknown_status",
                severity="warning",
                message=f"Unknown execution status '{raw_exec}' preserved",
                field="execution_status",
                raw_value=raw_exec
            ))
        exec_status = exec_status or "Not Started"

        raw_inv = raw.get("Invoice Status")
        inv_status, _, _ = map_category(raw_inv, self.wo_invoice_status_config)

        raw_bill = raw.get("Billing Status")
        bill_status, _, _ = map_category(raw_bill, self.wo_billing_status_config)

        owner = clean_text(raw.get("BD/KAM Personnel code"))

        return CanonicalWorkOrderRecord(
            source_system="Excel",
            source_file=source_file,
            source_sheet=source_sheet,
            source_row_number=row_num,
            source_record_id=source_rec_id,
            work_order_id=work_order_id,
            work_order_name=wo_name,
            deal_reference=deal_reference,
            customer=customer,
            sector=sector,
            nature_of_work=nature_of_work,
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
            raw_values={k: str(v) for k, v in raw.items()},
            quality_flags=flags,
            excluded_from_metrics=len(exclusion_reasons) > 0,
            exclusion_reasons=exclusion_reasons
        )
