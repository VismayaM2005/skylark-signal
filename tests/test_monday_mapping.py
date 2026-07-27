import pytest
from skylark_signal.monday.mapper import BoardSchemaMapper
from skylark_signal.monday.schemas import MondayBoard, MondayColumn, MondayItem, MondayColumnValue

def test_renamed_and_alias_column_mapping():
    mapper = BoardSchemaMapper()

    # Board with renamed / custom titles
    board = MondayBoard(
        id="111",
        name="Deals Custom Board",
        columns=[
            MondayColumn(id="col_name", title="Opportunity Title", type="name"), # matches alias 'opportunity'
            MondayColumn(id="col_cust", title="Client Account Code", type="text"), # matches alias 'client code'
            MondayColumn(id="col_val", title="Estimated Amount", type="numbers"), # matches alias 'amount'
            MondayColumn(id="col_stage", title="Funnel Stage", type="status"), # matches alias 'funnel stage'
            MondayColumn(id="col_extra", title="Internal Code XYZ", type="text") # unmapped extra column
        ]
    )

    report, field_map = mapper.inspect_and_map_schema(board, is_deals_board=True)

    assert report.board_id == "111"
    assert "deal_name" in field_map
    assert field_map["deal_name"].id == "col_name"
    assert field_map["customer"].id == "col_cust"
    assert field_map["deal_value"].id == "col_val"

    # Unmapped extra column reporting
    assert "Internal Code XYZ" in report.unmapped_monday_columns

    # Unresolved canonical field reporting
    assert "expected_close_date" in report.unresolved_canonical_fields
    assert "actual_close_date" in report.unresolved_canonical_fields

def test_deal_item_mapping_to_canonical_record():
    mapper = BoardSchemaMapper()

    board = MondayBoard(
        id="111",
        name="Deals Custom Board",
        columns=[
            MondayColumn(id="col_name", title="Opportunity Title", type="name"),
            MondayColumn(id="col_cust", title="Client Account Code", type="text"),
            MondayColumn(id="col_val", title="Estimated Amount", type="numbers")
        ]
    )
    report, field_map = mapper.inspect_and_map_schema(board, is_deals_board=True)

    item = MondayItem(
        id="500",
        name="Deal Beta",
        column_values=[
            MondayColumnValue(id="col_cust", title="Client Account Code", text="WOCOMPANY_005"),
            MondayColumnValue(id="col_val", title="Estimated Amount", text="750,000.00")
        ]
    )

    rec = mapper.map_monday_deal_item(item, board, field_map)

    assert rec.source_system == "monday.com API"
    assert rec.source_file == "monday_board_111"
    assert rec.deal_name == "Deal Beta"
    assert rec.customer == "COMPANY_005"
    assert rec.deal_value == 750000.0
    assert rec.deal_id.startswith("IMPORT-DEAL-")
    assert rec.raw_values["Client Account Code"] == "WOCOMPANY_005"
