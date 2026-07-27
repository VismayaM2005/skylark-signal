import os, json
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any
from skylark_signal.config import config
from skylark_signal.data.models import CanonicalDealRecord, CanonicalWorkOrderRecord
from skylark_signal.data.repository import MondayRepository

class DashboardRepository:
    """
    Data repository layer for Streamlit dashboard & agent queries.
    Provides live monday.com API fetching with seamless fallback to processed JSON files.
    """
    def __init__(
        self,
        deals_json_path: str = "data/processed/deals_clean.json",
        wo_json_path: str = "data/processed/work_orders_clean.json"
    ):
        self.deals_json_path = deals_json_path
        self.wo_json_path = wo_json_path
        self.status_info: Dict[str, Any] = {}

    def _load_from_json(self) -> Tuple[List[CanonicalDealRecord], List[CanonicalWorkOrderRecord]]:
        """Loads canonical records from local processed JSON files."""
        with open(self.deals_json_path, 'r', encoding='utf-8') as f:
            deals_raw = json.load(f)
        deals = [CanonicalDealRecord(**item) for item in deals_raw]

        with open(self.wo_json_path, 'r', encoding='utf-8') as f:
            wo_raw = json.load(f)
        work_orders = [CanonicalWorkOrderRecord(**item) for item in wo_raw]

        self.status_info = {
            "mode": "PROCESSED_JSON_FALLBACK",
            "mode_label": "Processed Data Snapshot",
            "is_live": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "deals_count": len(deals),
            "work_orders_count": len(work_orders),
            "source_description": "Clean import files (data/processed/)"
        }
        return deals, work_orders

    def load_data(self) -> Tuple[List[CanonicalDealRecord], List[CanonicalWorkOrderRecord], Dict[str, Any]]:
        """
        Attempts to load live monday.com data if token is set, else falls back to processed JSON.
        Returns (deals_list, work_orders_list, status_info_dict).
        """
        token_set = bool(config.monday_api_token and config.monday_deals_board_id and config.monday_work_orders_board_id)

        if token_set:
            try:
                repo = MondayRepository()
                deals_snap = repo.fetch_deals_snapshot()
                wo_snap = repo.fetch_work_orders_snapshot()
                
                deals = deals_snap.canonical_records
                work_orders = wo_snap.canonical_records

                self.status_info = {
                    "mode": "LIVE_MONDAY_API",
                    "mode_label": "Live monday.com GraphQL API",
                    "is_live": True,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "deals_count": len(deals),
                    "work_orders_count": len(work_orders),
                    "source_description": f"Live monday boards (Deals: {config.monday_deals_board_id}, WO: {config.monday_work_orders_board_id})"
                }
                return deals, work_orders, self.status_info
            except Exception as e:
                # Log warning and fall back to local JSON
                deals, work_orders = self._load_from_json()
                self.status_info["fallback_reason"] = str(e)
                return deals, work_orders, self.status_info
        else:
            deals, work_orders = self._load_from_json()
            return deals, work_orders, self.status_info
