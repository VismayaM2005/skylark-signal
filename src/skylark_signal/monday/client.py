import time
import requests
from typing import Dict, Any, Optional, List, Tuple
from skylark_signal.config import config
from skylark_signal.monday.queries import GET_BOARDS_METADATA, GET_BOARD_ITEMS_PAGINATED
from skylark_signal.monday.pagination import CursorPaginator
from skylark_signal.monday.schemas import MondayBoard, MondayColumn
from skylark_signal.monday.errors import (
    MondayAPIError,
    MondayAuthError,
    MondayPermissionError,
    MondayBoardNotFoundError,
    MondayRateLimitError,
    MondayTimeoutError,
    MondayMalformedResponseError
)

class MondayClient:
    """
    Read-only GraphQL API Client for monday.com.
    Enforces strict read-only access, handles retries, rate limiting, and response caching.
    """
    def __init__(
        self,
        api_token: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        cache_ttl: Optional[int] = None
    ):
        self.api_token = api_token or config.monday_api_token
        self.api_url = api_url or config.monday_api_url
        self.timeout = timeout if timeout is not None else config.monday_api_timeout
        self.max_retries = max_retries if max_retries is not None else config.monday_max_retries
        self.cache_ttl = cache_ttl if cache_ttl is not None else config.monday_cache_ttl
        
        # TTL Cache: cache_key -> (timestamp, response_data)
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def _validate_read_only(self, query: str):
        """Enforces read-only access by rejecting any query containing 'mutation'."""
        if "mutation" in query.lower():
            raise MondayPermissionError("Write operations and GraphQL mutations are strictly prohibited in Skylark Signal.")

    def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Executes a read-only GraphQL query against monday.com with retries and TTL caching.
        """
        self._validate_read_only(query)
        
        if not self.api_token:
            raise MondayAuthError("MONDAY_API_TOKEN environment variable is not set.")
            
        cache_key = f"{query}:{json_dumps_safe(variables)}"
        now = time.time()
        
        if use_cache and cache_key in self._cache:
            ts, cached_data = self._cache[cache_key]
            if now - ts < self.cache_ttl:
                return cached_data

        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
        
        payload = {"query": query, "variables": variables or {}}
        
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # Check HTTP status codes
                if resp.status_code == 401:
                    raise MondayAuthError("Authentication failed: Invalid or expired MONDAY_API_TOKEN (HTTP 401).")
                elif resp.status_code == 403:
                    raise MondayPermissionError("Forbidden: Insufficient permissions for requested monday.com resource (HTTP 403).")
                elif resp.status_code == 429:
                    if attempt < self.max_retries:
                        backoff = 2 ** attempt
                        time.sleep(backoff)
                        continue
                    raise MondayRateLimitError("Rate limit exceeded on monday.com API (HTTP 429).")
                elif resp.status_code in (500, 502, 503, 504):
                    if attempt < self.max_retries:
                        backoff = 2 ** attempt
                        time.sleep(backoff)
                        continue
                    resp.raise_for_status()
                    
                resp.raise_for_status()
                
                try:
                    data = resp.json()
                except Exception as e:
                    raise MondayMalformedResponseError(f"Failed to parse JSON response from monday.com: {e}")
                    
                # Check GraphQL level errors
                if "errors" in data:
                    errs = data["errors"]
                    err_msg = str(errs)
                    if any("complexity" in err_msg.lower() or "rate" in err_msg.lower() for err in errs):
                        if attempt < self.max_retries:
                            time.sleep(2 ** attempt)
                            continue
                        raise MondayRateLimitError(f"Complexity limit exceeded: {err_msg}")
                    elif any("unauthorized" in err_msg.lower() or "invalid token" in err_msg.lower() for err in errs):
                        raise MondayAuthError(f"monday.com authentication error: {err_msg}")
                    else:
                        raise MondayAPIError(f"monday.com GraphQL error: {err_msg}")
                        
                if "data" not in data:
                    raise MondayMalformedResponseError("Response missing required 'data' field.")
                    
                result_data = data["data"]
                if use_cache:
                    self._cache[cache_key] = (now, result_data)
                return result_data

            except (requests.Timeout, requests.exceptions.Timeout) as e:
                last_exception = MondayTimeoutError(f"Request to monday.com API timed out ({self.timeout}s): {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
            except requests.RequestException as e:
                last_exception = MondayAPIError(f"Network error connecting to monday.com API: {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue

        if last_exception:
            raise last_exception
        raise MondayAPIError("Unknown error during GraphQL query execution.")

    def fetch_board_metadata(self, board_id: str) -> MondayBoard:
        """Fetches board metadata (columns, name, description)."""
        data = self.execute_query(GET_BOARDS_METADATA, {"board_ids": [board_id]})
        boards = data.get("boards", [])
        if not boards:
            raise MondayBoardNotFoundError(f"Board with ID '{board_id}' was not found on monday.com.")
            
        b = boards[0]
        columns = [
            MondayColumn(
                id=str(c.get("id")),
                title=str(c.get("title", "")),
                type=str(c.get("type", "text")),
                settings_str=c.get("settings_str")
            )
            for c in b.get("columns", [])
        ]
        
        return MondayBoard(
            id=str(b.get("id")),
            name=str(b.get("name", "")),
            description=b.get("description"),
            columns=columns,
            items=[],
            items_count=0
        )

    def fetch_board_items_page(
        self,
        board_id: str,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetches a single page of board items using cursor pagination."""
        vars_dict = {"board_id": board_id, "limit": limit}
        if cursor:
            vars_dict["cursor"] = cursor
        return self.execute_query(GET_BOARD_ITEMS_PAGINATED, vars_dict, use_cache=False)

    def fetch_full_board(self, board_id: str, limit: int = 100) -> MondayBoard:
        """Fetches metadata and all items from a board using cursor pagination."""
        paginator = CursorPaginator(self.fetch_board_items_page)
        board, _ = paginator.fetch_all_items(board_id, limit=limit)
        if not board.items:
            # We preserve empty board state or raise error if needed
            pass
        return board

def json_dumps_safe(obj: Any) -> str:
    """Deterministic json string helper."""
    import json
    try:
        return json.dumps(obj, sort_keys=True)
    except Exception:
        return str(obj)
