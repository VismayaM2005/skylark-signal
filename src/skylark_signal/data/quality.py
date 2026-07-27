from typing import Optional, Literal, Any
from pydantic import BaseModel, Field

class QualityFlag(BaseModel):
    """Structured data quality flag representation."""
    code: str = Field(..., description="Unique error or warning code e.g. missing_deal_value")
    severity: Literal["info", "warning", "error"] = Field(..., description="Flag severity level")
    field: Optional[str] = Field(None, description="Affected field name")
    message: str = Field(..., description="Human readable message describing the issue")
    raw_value: Optional[Any] = Field(None, description="Original raw value that triggered the flag")
    affects_metrics: bool = Field(False, description="Whether this issue prevents safely using the record in BI metrics")
    recommended_action: Optional[str] = Field(None, description="Action recommended to resolve the issue")

def create_quality_flag(
    code: str,
    severity: Literal["info", "warning", "error"],
    message: str,
    field: Optional[str] = None,
    raw_value: Optional[Any] = None,
    affects_metrics: bool = False,
    recommended_action: Optional[str] = None
) -> QualityFlag:
    return QualityFlag(
        code=code,
        severity=severity,
        field=field,
        message=message,
        raw_value=str(raw_value) if raw_value is not None else None,
        affects_metrics=affects_metrics,
        recommended_action=recommended_action
    )
