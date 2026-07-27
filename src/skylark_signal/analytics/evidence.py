from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvidenceRecord(BaseModel):
    """Micro-evidence object linking a calculated metric or risk item back to source records."""
    metric_name: str = Field(..., description="Name of the metric or risk item e.g. total_open_pipeline")
    source_system: str = Field("monday.com", description="Source system e.g. monday.com API or Excel")
    board_name: str = Field(..., description="Source board name e.g. Deals or Work Orders")
    source_item_id: str = Field(..., description="Source item ID e.g. Monday item ID or row number")
    source_record_id: str = Field(..., description="Source record ID e.g. SRC-REC-XXX")
    field_name: str = Field(..., description="Target field evaluated e.g. deal_value, execution_status")
    raw_value: Optional[str] = Field(None, description="Raw unparsed source value")
    normalized_value: Optional[Any] = Field(None, description="Clean normalized value")
    included_in_calculation: bool = Field(True, description="Whether record was included in metric sum/count")
    inclusion_reason: str = Field("Record met criteria", description="Why record was included")
    exclusion_reason: Optional[str] = Field(None, description="Why record was excluded if applicable")

class EvidenceCollector:
    """Collector for accumulating micro-evidence records across metrics generation."""
    def __init__(self):
        self._records: List[EvidenceRecord] = []

    def add_evidence(
        self,
        metric_name: str,
        board_name: str,
        source_item_id: str,
        source_record_id: str,
        field_name: str,
        raw_value: Optional[str] = None,
        normalized_value: Optional[Any] = None,
        included_in_calculation: bool = True,
        inclusion_reason: str = "Record met criteria",
        exclusion_reason: Optional[str] = None,
        source_system: str = "monday.com"
    ):
        rec = EvidenceRecord(
            metric_name=metric_name,
            source_system=source_system,
            board_name=board_name,
            source_item_id=str(source_item_id),
            source_record_id=str(source_record_id),
            field_name=field_name,
            raw_value=str(raw_value) if raw_value is not None else None,
            normalized_value=normalized_value,
            included_in_calculation=included_in_calculation,
            inclusion_reason=inclusion_reason,
            exclusion_reason=exclusion_reason
        )
        self._records.append(rec)

    def get_evidence_for_metric(self, metric_name: str) -> List[EvidenceRecord]:
        return [r for r in self._records if r.metric_name == metric_name]

    def get_all_evidence(self) -> List[EvidenceRecord]:
        return self._records

    def count_by_metric(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for r in self._records:
            counts[r.metric_name] = counts.get(r.metric_name, 0) + 1
        return counts
