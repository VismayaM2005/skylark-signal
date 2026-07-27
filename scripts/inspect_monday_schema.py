import os, sys, json
# Add src directory to path
sys.path.insert(0, os.path.abspath("src"))

from skylark_signal.config import config
from skylark_signal.monday.client import MondayClient
from skylark_signal.monday.mapper import BoardSchemaMapper
from skylark_signal.monday.schemas import MondayBoard, MondayColumn, MondayItem, MondayColumnValue
from skylark_signal.data.repository import MondayRepository

def create_mock_deals_board() -> MondayBoard:
    """Creates a simulated Deals board for schema testing when API token is unset."""
    return MondayBoard(
        id="1234567890",
        name="Deals Board (Simulated)",
        description="Simulated Deals board for schema inspection",
        columns=[
            MondayColumn(id="name", title="Deal Name", type="name"),
            MondayColumn(id="text0", title="Customer Code", type="text"),
            MondayColumn(id="text1", title="Sector/Service", type="text"),
            MondayColumn(id="status0", title="Deal Stage", type="status"),
            MondayColumn(id="status1", title="Deal Status", type="status"),
            MondayColumn(id="numbers0", title="Masked Deal Value", type="numbers"),
            MondayColumn(id="numbers1", title="Closure Probability", type="numbers"),
            MondayColumn(id="date0", title="Tentative Close Date", type="date"),
            MondayColumn(id="date1", title="Close Date (A)", type="date"),
            MondayColumn(id="text2", title="Owner Code", type="text"),
            MondayColumn(id="text3", title="Product Deal", type="text"),
            MondayColumn(id="text4", title="Custom Internal Flag", type="text") # Unmapped extra column
        ],
        items=[
            MondayItem(
                id="101",
                name="Project Alpha",
                column_values=[
                    MondayColumnValue(id="text0", title="Customer Code", text="COMPANY005"),
                    MondayColumnValue(id="text1", title="Sector/Service", text="Mining"),
                    MondayColumnValue(id="status0", title="Deal Stage", text="G. Project Won"),
                    MondayColumnValue(id="status1", title="Deal Status", text="Won"),
                    MondayColumnValue(id="numbers0", title="Masked Deal Value", text="500000"),
                    MondayColumnValue(id="numbers1", title="Closure Probability", text="0.8")
                ]
            )
        ],
        items_count=1
    )

def create_mock_work_orders_board() -> MondayBoard:
    """Creates a simulated Work Orders board for schema testing when API token is unset."""
    return MondayBoard(
        id="9876543210",
        name="Work Orders Board (Simulated)",
        description="Simulated Work Orders board for schema inspection",
        columns=[
            MondayColumn(id="name", title="Deal Name Masked", type="name"),
            MondayColumn(id="text0", title="Customer Name Code", type="text"),
            MondayColumn(id="text1", title="Serial #", type="text"),
            MondayColumn(id="text2", title="Nature of Work", type="text"),
            MondayColumn(id="status0", title="Execution Status", type="status"),
            MondayColumn(id="numbers0", title="Amount in Rupees (Excl of GST) (Masked)", type="numbers"),
            MondayColumn(id="numbers1", title="Amount in Rupees (Incl of GST) (Masked)", type="numbers"),
            MondayColumn(id="date0", title="Probable Start Date", type="date"),
            MondayColumn(id="date1", title="Probable End Date", type="date"),
            MondayColumn(id="text3", title="BD/KAM Personnel Code", type="text")
        ],
        items=[
            MondayItem(
                id="201",
                name="Work Order 201",
                column_values=[
                    MondayColumnValue(id="text0", title="Customer Name Code", text="WOCOMPANY_002"),
                    MondayColumnValue(id="text1", title="Serial #", text="SDPLDEAL-075"),
                    MondayColumnValue(id="status0", title="Execution Status", text="Completed"),
                    MondayColumnValue(id="numbers0", title="Amount in Rupees (Excl of GST) (Masked)", text="100000"),
                    MondayColumnValue(id="numbers1", title="Amount in Rupees (Incl of GST) (Masked)", text="118000")
                ]
            )
        ],
        items_count=1
    )

def main():
    print("=== SKYLARK SIGNAL MONDAY.COM SCHEMA INSPECTION ===")
    token_set = bool(config.monday_api_token)
    print(f"API Token Status: {'SET (' + config.masked_token + ')' if token_set else 'UNSET (Running in Dry-Run / Mock Mode)'}")
    print(f"Deals Board ID: {config.monday_deals_board_id or 'NOT CONFIGURED'}")
    print(f"Work Orders Board ID: {config.monday_work_orders_board_id or 'NOT CONFIGURED'}\n")

    mapper = BoardSchemaMapper()

    if token_set and config.monday_deals_board_id and config.monday_work_orders_board_id:
        print("Connecting to live monday.com API...\n")
        try:
            repo = MondayRepository()
            deals_snap = repo.fetch_deals_snapshot()
            wo_snap = repo.fetch_work_orders_snapshot()
            
            deals_board = deals_snap.board_metadata
            wo_board = wo_snap.board_metadata
        except Exception as e:
            print(f"Error connecting to live API: {e}")
            print("Falling back to simulated inspection...\n")
            deals_board = create_mock_deals_board()
            wo_board = create_mock_work_orders_board()
    else:
        print("Running in simulated inspection mode...\n")
        deals_board = create_mock_deals_board()
        wo_board = create_mock_work_orders_board()

    # Inspect Deals Board
    print("--------------------------------------------------")
    print(f"DEALS BOARD METADATA: [{deals_board.id}] {deals_board.name}")
    print(f"Total Columns: {len(deals_board.columns)} | Items Count: {deals_board.items_count}")
    deals_report, field_map_deals = mapper.inspect_and_map_schema(deals_board, is_deals_board=True)
    print(f"Overall Mapping Confidence Score: {deals_report.overall_confidence * 100:.2f}%")
    print(f"Unresolved Canonical Fields ({len(deals_report.unresolved_canonical_fields)}): {deals_report.unresolved_canonical_fields}")
    print(f"Unmapped Monday Columns ({len(deals_report.unmapped_monday_columns)}): {deals_report.unmapped_monday_columns}")
    
    print("\nColumn Mapping Details (Deals):")
    for res in deals_report.mapped_columns:
        status_symbol = "OK" if res.confidence_score >= 0.70 else "MISSING"
        col_info = f"-> {res.monday_column_title} ({res.monday_column_id})" if res.monday_column_id else "(UNMAPPED)"
        print(f"  [{status_symbol:7s}] {res.canonical_field:22s} {col_info:35s} [Score: {res.confidence_score:.2f} | Rule: {res.mapping_rule}]")

    # Inspect Work Orders Board
    print("\n--------------------------------------------------")
    print(f"WORK ORDERS BOARD METADATA: [{wo_board.id}] {wo_board.name}")
    print(f"Total Columns: {len(wo_board.columns)} | Items Count: {wo_board.items_count}")
    wo_report, field_map_wo = mapper.inspect_and_map_schema(wo_board, is_deals_board=False)
    print(f"Overall Mapping Confidence Score: {wo_report.overall_confidence * 100:.2f}%")
    print(f"Unresolved Canonical Fields ({len(wo_report.unresolved_canonical_fields)}): {wo_report.unresolved_canonical_fields}")
    print(f"Unmapped Monday Columns ({len(wo_report.unmapped_monday_columns)}): {wo_report.unmapped_monday_columns}")
    
    print("\nColumn Mapping Details (Work Orders):")
    for res in wo_report.mapped_columns:
        status_symbol = "OK" if res.confidence_score >= 0.70 else "MISSING"
        col_info = f"-> {res.monday_column_title} ({res.monday_column_id})" if res.monday_column_id else "(UNMAPPED)"
        print(f"  [{status_symbol:7s}] {res.canonical_field:22s} {col_info:35s} [Score: {res.confidence_score:.2f} | Rule: {res.mapping_rule}]")

    print("\n=== SCHEMA INSPECTION COMPLETE ===")

if __name__ == "__main__":
    main()
