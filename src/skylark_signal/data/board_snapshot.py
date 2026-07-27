from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from skylark_signal.monday.schemas import MondayBoard, SchemaMappingReport

class BoardSnapshot(BaseModel):
    """Container representing a point-in-time snapshot of a monday.com board."""
    board_id: str = Field(..., description="Board ID")
    board_name: str = Field(..., description="Board Name")
    snapshot_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when snapshot was taken"
    )
    board_metadata: MondayBoard = Field(..., description="Full board metadata and raw items")
    canonical_records: List[Any] = Field(default_factory=list, description="Normalized canonical records")
    schema_mapping_report: SchemaMappingReport = Field(..., description="Schema column mapping report")
    unresolved_columns: List[str] = Field(default_factory=list, description="Unmapped / unresolved columns list")

    @property
    def record_count(self) -> int:
        return len(self.canonical_records)
