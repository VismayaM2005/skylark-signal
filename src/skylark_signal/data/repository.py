from typing import Optional, Tuple, List, Dict, Any
from skylark_signal.config import config
from skylark_signal.monday.client import MondayClient
from skylark_signal.monday.mapper import BoardSchemaMapper
from skylark_signal.monday.schemas import MondayBoard, SchemaMappingReport
from skylark_signal.monday.errors import MondayBoardNotFoundError
from skylark_signal.data.board_snapshot import BoardSnapshot
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord

class MondayRepository:
    """
    Repository layer for retrieving board snapshots and canonical records from monday.com.
    """
    def __init__(
        self,
        client: Optional[MondayClient] = None,
        mapper: Optional[BoardSchemaMapper] = None
    ):
        self.client = client or MondayClient()
        self.mapper = mapper or BoardSchemaMapper()

    def fetch_deals_snapshot(self, board_id: Optional[str] = None) -> BoardSnapshot:
        """Fetches and maps the Deals board into a BoardSnapshot."""
        target_board_id = board_id or config.monday_deals_board_id
        if not target_board_id:
            raise MondayBoardNotFoundError("MONDAY_DEALS_BOARD_ID is not configured in environment or arguments.")
            
        board = self.client.fetch_full_board(target_board_id)
        report, field_to_col = self.mapper.inspect_and_map_schema(board, is_deals_board=True)
        
        canonical_records = [
            self.mapper.map_monday_deal_item(item, board, field_to_col)
            for item in board.items
        ]
        
        return BoardSnapshot(
            board_id=board.id,
            board_name=board.name,
            board_metadata=board,
            canonical_records=canonical_records,
            schema_mapping_report=report,
            unresolved_columns=report.unresolved_canonical_fields
        )

    def fetch_work_orders_snapshot(self, board_id: Optional[str] = None) -> BoardSnapshot:
        """Fetches and maps the Work Orders board into a BoardSnapshot."""
        target_board_id = board_id or config.monday_work_orders_board_id
        if not target_board_id:
            raise MondayBoardNotFoundError("MONDAY_WORK_ORDERS_BOARD_ID is not configured in environment or arguments.")
            
        board = self.client.fetch_full_board(target_board_id)
        report, field_to_col = self.mapper.inspect_and_map_schema(board, is_deals_board=False)
        
        canonical_records = [
            self.mapper.map_monday_work_order_item(item, board, field_to_col)
            for item in board.items
        ]
        
        return BoardSnapshot(
            board_id=board.id,
            board_name=board.name,
            board_metadata=board,
            canonical_records=canonical_records,
            schema_mapping_report=report,
            unresolved_columns=report.unresolved_canonical_fields
        )

    def get_all_snapshots(
        self,
        deals_board_id: Optional[str] = None,
        wo_board_id: Optional[str] = None
    ) -> Dict[str, BoardSnapshot]:
        """Fetches both Deals and Work Orders snapshots."""
        deals_snapshot = self.fetch_deals_snapshot(deals_board_id)
        wo_snapshot = self.fetch_work_orders_snapshot(wo_board_id)
        return {
            "deals": deals_snapshot,
            "work_orders": wo_snapshot
        }
