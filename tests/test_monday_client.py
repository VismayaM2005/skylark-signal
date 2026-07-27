import pytest
from unittest.mock import patch, MagicMock
from skylark_signal.config import Config
from skylark_signal.monday.client import MondayClient
from skylark_signal.monday.errors import (
    MondayAuthError,
    MondayPermissionError,
    MondayBoardNotFoundError,
    MondayRateLimitError,
    MondayTimeoutError
)

def test_token_masking():
    cfg = Config()
    cfg.monday_api_token = "secret_token_123456789"
    assert cfg.masked_token == "***6789"
    assert "secret_token" not in repr(cfg)

def test_read_only_mutation_rejection():
    client = MondayClient(api_token="test_token")
    mutation_query = "mutation { create_item (board_id: 123, item_name: 'test') { id } }"
    with pytest.raises(MondayPermissionError, match="strictly prohibited"):
        client.execute_query(mutation_query)

def test_missing_api_token():
    client = MondayClient(api_token=None)
    with pytest.raises(MondayAuthError, match="not set"):
        client.execute_query("query { me { id } }")

@patch("requests.post")
def test_successful_query_execution(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"me": {"id": 100, "name": "User"}}}
    mock_post.return_value = mock_resp

    client = MondayClient(api_token="test_token")
    data = client.execute_query("query { me { id name } }", use_cache=False)
    assert data["me"]["id"] == 100

@patch("requests.post")
def test_auth_error_http_401(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_post.return_value = mock_resp

    client = MondayClient(api_token="bad_token", max_retries=0)
    with pytest.raises(MondayAuthError, match="401"):
        client.execute_query("query { me { id } }", use_cache=False)

@patch("requests.post")
def test_rate_limit_http_429(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_post.return_value = mock_resp

    client = MondayClient(api_token="test_token", max_retries=1)
    with pytest.raises(MondayRateLimitError, match="429"):
        client.execute_query("query { me { id } }", use_cache=False)

@patch("requests.post")
def test_fetch_board_metadata_not_found(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"boards": []}}
    mock_post.return_value = mock_resp

    client = MondayClient(api_token="test_token")
    with pytest.raises(MondayBoardNotFoundError, match="not found"):
        client.fetch_board_metadata("99999")

@patch("requests.post")
def test_response_ttl_caching(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"boards": [{"id": "100", "name": "Cached Board"}]}}
    mock_post.return_value = mock_resp

    client = MondayClient(api_token="test_token", cache_ttl=10)
    
    # First call - makes HTTP request
    d1 = client.execute_query("query { boards { id name } }", use_cache=True)
    assert mock_post.call_count == 1

    # Second call - served from cache
    d2 = client.execute_query("query { boards { id name } }", use_cache=True)
    assert mock_post.call_count == 1
    assert d1 == d2
