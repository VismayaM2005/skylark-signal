"""GraphQL Query templates for monday.com v2 API."""

GET_BOARDS_METADATA = """
query GetBoardMetadata($board_ids: [ID!]!) {
  boards(ids: $board_ids) {
    id
    name
    description
    columns {
      id
      title
      type
      settings_str
    }
  }
}
"""

GET_BOARD_ITEMS_PAGINATED = """
query GetBoardItemsPaginated($board_id: ID!, $limit: Int!, $cursor: String) {
  boards(ids: [$board_id]) {
    id
    name
    description
    columns {
      id
      title
      type
      settings_str
    }
    items_page(limit: $limit, cursor: $cursor) {
      cursor
      items {
        id
        name
        created_at
        updated_at
        column_values {
          id
          type
          text
          value
        }
      }
    }
  }
}
"""
