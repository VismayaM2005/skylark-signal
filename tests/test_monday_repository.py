import pytest
from unittest.mock import MagicMock
from skylark_signal.monday.schemas import MondayBoard, MondayColumn, MondayItem, MondayColumnValue
from skylark_signal.data.repository import MondayRepository

def test_repository_fetch_deals_snapshot():
    mock_client = MagicMock()
    mock_board = MondayBoard(
        id="1001",
        name="Deals Live Board",
        columns=[
            MondayColumn(id="c_name", title="Deal Name", type="name"),
            MondayColumn(id="c_cust", title="Customer Code", type="text"),
            MondayColumn(id="c_val", title="Masked Deal Value", type="numbers")
        ],
        items=[
            MondayItem(
                id="777",
                name="Deal Gamma",
                column_values=[
                    MondayColumnValue(id="c_cust", title="Customer Code", text="COMPANY010"),
                    MondayColumnValue(id="c_val", title="Masked Deal Value", text="250000")
                ]
            )
        ],
        items_count=1
    )
    mock_client.fetch_full_board.return_value = mock_board

    repo = MondayRepository(client=mock_client)
    snapshot = repo.fetch_deals_snapshot(board_id="1001")

    assert snapshot.board_id == "1001"
    assert snapshot.board_name == "Deals Live Board"
    assert snapshot.record_count == 1
    
    rec = snapshot.canonical_records[0]
    assert rec.deal_name == "Deal Gamma"
    assert rec.customer == "COMPANY_010"
    assert rec.deal_value == 250000.0
    assert rec.source_file == "monday_board_1001"

def test_repository_fetch_work_orders_snapshot_no_fake_deal_reference():
    mock_client = MagicMock()
    mock_board = MondayBoard(
        id="2002",
        name="Work Orders Live Board",
        columns=[
            MondayColumn(id="c_name", title="Deal Name Masked", type="name"),
            MondayColumn(id="c_cust", title="Customer Name Code", type="text"),
            MondayColumn(id="c_wo_id", title="Serial #", type="text"),
            MondayColumn(id="c_excl", title="Amount in Rupees (Excl of GST) (Masked)", type="numbers")
        ],
        items=[
            MondayItem(
                id="888",
                name="Work Order Delta",
                column_values=[
                    MondayColumnValue(id="c_cust", title="Customer Name Code", text="WOCOMPANY_002"),
                    MondayColumnValue(id="c_wo_id", title="Serial #", text="SDPLDEAL-100"),
                    MondayColumnValue(id="c_excl", title="Amount in Rupees (Excl of GST) (Masked)", text="150000")
                ]
            )
        ],
        items_count=1
    )
    mock_client.fetch_full_board.return_value = mock_board

    repo = MondayRepository(client=mock_client)
    snapshot = repo.fetch_work_orders_snapshot(board_id="2002")

    assert snapshot.board_id == "2002"
    assert snapshot.record_count == 1

    rec = snapshot.canonical_records[0]
    assert rec.work_order_id == "SDPLDEAL-100"
    assert rec.work_order_name == "Work Order Delta"
    assert rec.customer == "COMPANY_002"
    assert rec.deal_reference is None # MUST REMAIN NONE
    assert rec.project_value_excl_tax == 150000.0
