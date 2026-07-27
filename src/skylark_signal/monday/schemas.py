from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class MondayColumn(BaseModel):
    """Represents column metadata from a monday.com board."""
    id: str = Field(..., description="Column ID on monday.com e.g. text0")
    title: str = Field(..., description="Human readable column title")
    type: str = Field(..., description="monday.com column type e.g. text, numbers, status, date")
    settings_str: Optional[str] = Field(None, description="Raw settings JSON string if available")

class MondayColumnValue(BaseModel):
    """Represents a column value for an item on monday.com."""
    id: str = Field(..., description="Column ID matching MondayColumn.id")
    title: Optional[str] = Field(None, description="Column title if available")
    text: Optional[str] = Field(None, description="Display text representation")
    value: Optional[str] = Field(None, description="Raw JSON string value from monday.com API")
    type: Optional[str] = Field(None, description="Column type")

class MondayItem(BaseModel):
    """Represents an item row on a monday.com board."""
    id: str = Field(..., description="Monday Item ID")
    name: str = Field(..., description="Item title / name")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    column_values: List[MondayColumnValue] = Field(default_factory=list, description="List of column values")

class MondayBoard(BaseModel):
    """Represents a full monday.com board snapshot."""
    id: str = Field(..., description="Board ID")
    name: str = Field(..., description="Board Name")
    description: Optional[str] = Field(None, description="Board description")
    columns: List[MondayColumn] = Field(default_factory=list, description="Board column metadata")
    items: List[MondayItem] = Field(default_factory=list, description="Board items list")
    items_count: int = Field(0, description="Total items count")

class ColumnMappingResult(BaseModel):
    """Represents a mapped relationship between a canonical field and a monday column."""
    canonical_field: str = Field(..., description="Canonical field name e.g. deal_value")
    monday_column_id: Optional[str] = Field(None, description="Mapped monday column ID")
    monday_column_title: Optional[str] = Field(None, description="Mapped monday column title")
    monday_column_type: Optional[str] = Field(None, description="Mapped monday column type")
    confidence_score: float = Field(..., description="Mapping confidence between 0.0 and 1.0")
    mapping_rule: str = Field(..., description="Rule used for mapping e.g. exact_title_match, alias_match")

class SchemaMappingReport(BaseModel):
    """Report detailing column mapping coverage and unresolved fields for a board."""
    board_id: str = Field(..., description="Board ID")
    board_name: str = Field(..., description="Board Name")
    mapped_columns: List[ColumnMappingResult] = Field(default_factory=list, description="List of successfully mapped fields")
    unresolved_canonical_fields: List[str] = Field(default_factory=list, description="Canonical fields that could not be mapped")
    unmapped_monday_columns: List[str] = Field(default_factory=list, description="Monday columns that were not mapped to canonical fields")
    overall_confidence: float = Field(0.0, description="Average confidence score across required canonical fields")
