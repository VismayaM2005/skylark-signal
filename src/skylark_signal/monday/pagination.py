from typing import List, Dict, Any, Optional, Callable, Tuple
from skylark_signal.monday.schemas import MondayItem, MondayBoard, MondayColumn

class CursorPaginator:
    """Helper for fetching all items from a monday.com board using cursor pagination."""
    
    def __init__(self, fetch_page_fn: Callable[[str, int, Optional[str]], Dict[str, Any]]):
        self.fetch_page_fn = fetch_page_fn

    def fetch_all_items(self, board_id: str, limit: int = 100) -> Tuple[MondayBoard, List[str]]:
        """
        Iteratively fetches all items from a board using cursor pagination.
        Returns (MondayBoard, list_of_cursors_used)
        """
        all_items: List[MondayItem] = []
        cursors_used: List[str] = []
        cursor: Optional[str] = None
        
        board_metadata: Optional[Dict[str, Any]] = None
        
        while True:
            response_data = self.fetch_page_fn(board_id, limit, cursor)
            
            boards_data = response_data.get("boards", [])
            if not boards_data:
                break
                
            board_dict = boards_data[0]
            if board_metadata is None:
                board_metadata = {
                    "id": str(board_dict.get("id")),
                    "name": str(board_dict.get("name", f"Board {board_id}")),
                    "description": board_dict.get("description"),
                    "columns": board_dict.get("columns", [])
                }
                
            items_page = board_dict.get("items_page", {})
            raw_items = items_page.get("items", [])
            
            for raw_item in raw_items:
                col_vals = raw_item.get("column_values", [])
                item_model = MondayItem(
                    id=str(raw_item.get("id")),
                    name=str(raw_item.get("name", "")),
                    created_at=raw_item.get("created_at"),
                    updated_at=raw_item.get("updated_at"),
                    column_values=[
                        {
                            "id": str(cv.get("id")),
                            "title": cv.get("title"),
                            "text": cv.get("text"),
                            "value": cv.get("value"),
                            "type": cv.get("type")
                        }
                        for cv in col_vals
                    ]
                )
                all_items.append(item_model)
                
            next_cursor = items_page.get("cursor")
            if next_cursor:
                cursors_used.append(next_cursor)
                cursor = next_cursor
            else:
                break

        if board_metadata is None:
            board_metadata = {
                "id": str(board_id),
                "name": f"Board {board_id}",
                "description": None,
                "columns": []
            }
            
        columns = [
            MondayColumn(
                id=str(c.get("id")),
                title=str(c.get("title", "")),
                type=str(c.get("type", "text")),
                settings_str=c.get("settings_str")
            )
            for c in board_metadata.get("columns", [])
        ]
        
        board = MondayBoard(
            id=board_metadata["id"],
            name=board_metadata["name"],
            description=board_metadata.get("description"),
            columns=columns,
            items=all_items,
            items_count=len(all_items)
        )
        
        return board, cursors_used
