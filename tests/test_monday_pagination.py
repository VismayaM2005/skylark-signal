import pytest
from skylark_signal.monday.pagination import CursorPaginator

def test_cursor_pagination_multi_page():
    # Mock page fetcher function
    pages_data = {
        None: {
            "boards": [{
                "id": "123",
                "name": "Deals Board",
                "columns": [{"id": "c1", "title": "Deal Name", "type": "name"}],
                "items_page": {
                    "cursor": "cursor_page_2",
                    "items": [
                        {"id": "1", "name": "Item 1", "column_values": []},
                        {"id": "2", "name": "Item 2", "column_values": []}
                    ]
                }
            }]
        },
        "cursor_page_2": {
            "boards": [{
                "id": "123",
                "name": "Deals Board",
                "columns": [{"id": "c1", "title": "Deal Name", "type": "name"}],
                "items_page": {
                    "cursor": None, # End of pages
                    "items": [
                        {"id": "3", "name": "Item 3", "column_values": []}
                    ]
                }
            }]
        }
    }

    def mock_fetch_page(board_id, limit, cursor):
        return pages_data.get(cursor, {})

    paginator = CursorPaginator(mock_fetch_page)
    board, cursors = paginator.fetch_all_items("123", limit=2)

    assert board.id == "123"
    assert board.name == "Deals Board"
    assert len(board.items) == 3
    assert [i.id for i in board.items] == ["1", "2", "3"]
    assert cursors == ["cursor_page_2"]

def test_cursor_pagination_empty_board():
    empty_page = {
        "boards": [{
            "id": "456",
            "name": "Empty Board",
            "columns": [],
            "items_page": {
                "cursor": None,
                "items": []
            }
        }]
    }

    def mock_fetch_page(board_id, limit, cursor):
        return empty_page

    paginator = CursorPaginator(mock_fetch_page)
    board, cursors = paginator.fetch_all_items("456", limit=100)

    assert board.id == "456"
    assert len(board.items) == 0
    assert cursors == []
