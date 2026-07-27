import hashlib
from typing import Optional, Tuple

def get_file_sha256(filepath: str) -> str:
    """Computes SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def generate_source_record_id(file_hash: str, sheet_name: str, row_number: int) -> str:
    """
    Generates a deterministic source_record_id based on file hash, sheet name, and row number.
    Format: SRC-REC-<hash_prefix>-<row_number>
    """
    raw_str = f"{file_hash}:{sheet_name}:{row_number}"
    h = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:12].upper()
    return f"SRC-REC-{h}"

def generate_synthetic_deal_id(file_hash: str, row_number: int, deal_name: str, customer: str) -> str:
    """
    Generates a deterministic surrogate import key for Deals because Deals dataset lacks a source primary key.
    Format: IMPORT-DEAL-<hash_prefix>
    """
    raw_str = f"{file_hash}:{row_number}:{deal_name}:{customer}"
    h = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:12].upper()
    return f"IMPORT-DEAL-{h}"

def validate_work_order_id(wo_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validates work_order_id format e.g. SDPLDEAL-075.
    Returns (is_valid, warning_message)
    """
    if not wo_id:
        return False, "Missing Work Order ID (Serial #)"
    
    wo_str = str(wo_id).strip()
    if not wo_str or wo_str.lower() in ('nan', 'none', 'null'):
        return False, "Work Order ID is empty"
        
    return True, None
