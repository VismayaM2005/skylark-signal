import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from skylark_signal.data.identifiers import get_file_sha256

def load_deals_excel(filepath: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Ingests deals raw excel file.
    Detects repeated headers, blank rows, and duplicate business records.
    Preserves original Excel 1-based row numbers.
    Returns (usable_rows, repeated_header_rows, duplicate_business_rows, metrics)
    """
    file_hash = get_file_sha256(filepath)
    df_raw = pd.read_excel(filepath, sheet_name='Deal tracker')
    
    total_raw_rows = len(df_raw)
    total_raw_cols = len(df_raw.columns)
    
    usable_rows = []
    repeated_header_rows = []
    duplicate_rows = []
    
    seen_fingerprints = set()
    blank_row_count = 0
    repeated_header_count = 0
    duplicate_count = 0
    
    for idx, row in df_raw.iterrows():
        excel_row_num = idx + 2 # Header is at row index 1 in 1-based Excel indexing
        row_dict = row.to_dict()
        
        # Check blank row
        if row.isnull().all():
            blank_row_count += 1
            continue
            
        # Check repeated header row e.g. 'Deal Stage' == 'Deal Stage'
        d_stage = str(row_dict.get('Deal Stage', '')).strip()
        d_status = str(row_dict.get('Deal Status', '')).strip()
        d_sector = str(row_dict.get('Sector/service', '')).strip()
        
        if d_stage == 'Deal Stage' or d_status == 'Deal Status' or d_sector == 'Sector/service':
            repeated_header_count += 1
            repeated_header_rows.append({
                "source_row_number": excel_row_num,
                "reason": "Repeated embedded header row",
                "raw_values": {k: str(v) for k, v in row_dict.items()}
            })
            continue
            
        # Create fingerprint for duplicate detection
        row_str_tuple = tuple(str(row_dict.get(col, '')).strip() for col in df_raw.columns)
        if row_str_tuple in seen_fingerprints:
            duplicate_count += 1
            duplicate_rows.append({
                "source_row_number": excel_row_num,
                "reason": "Exact duplicate business record",
                "raw_values": {k: str(v) for k, v in row_dict.items()}
            })
            continue
            
        seen_fingerprints.add(row_str_tuple)
        usable_rows.append({
            "source_file": filepath,
            "source_sheet": "Deal tracker",
            "source_row_number": excel_row_num,
            "file_hash": file_hash,
            "raw_values": row_dict
        })
        
    metrics = {
        "dataset": "Deals",
        "file_hash": file_hash,
        "raw_worksheet_rows": total_raw_rows,
        "raw_worksheet_cols": total_raw_cols,
        "blank_rows_removed": blank_row_count,
        "repeated_header_rows_removed": repeated_header_count,
        "duplicate_business_rows_removed": duplicate_count,
        "usable_business_records": len(usable_rows)
    }
    
    return usable_rows, repeated_header_rows, duplicate_rows, metrics

def load_work_orders_excel(filepath: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Ingests work orders raw excel file.
    Handles blank first row (index 0) and header position at index 1.
    Preserves original Excel 1-based row numbers.
    Returns (usable_rows, rejected_rows, metrics)
    """
    file_hash = get_file_sha256(filepath)
    df_raw = pd.read_excel(filepath, sheet_name='work order tracker', header=None)
    
    total_raw_rows = len(df_raw)
    total_raw_cols = len(df_raw.columns)
    
    # Row index 0 is blank row, Row index 1 is header row
    headers = df_raw.iloc[1].values
    
    usable_rows = []
    rejected_rows = []
    
    blank_row_count = 1 # Row index 0
    duplicate_count = 0
    seen_fingerprints = set()
    
    for idx in range(2, total_raw_rows):
        excel_row_num = idx + 1 # 1-based Excel row number
        row_series = df_raw.iloc[idx]
        
        if row_series.isnull().all():
            blank_row_count += 1
            continue
            
        row_dict = {str(headers[i]).strip(): row_series.iloc[i] for i in range(len(headers))}
        
        # Duplicate check
        row_str_tuple = tuple(str(v).strip() for v in row_dict.values())
        if row_str_tuple in seen_fingerprints:
            duplicate_count += 1
            rejected_rows.append({
                "source_row_number": excel_row_num,
                "reason": "Exact duplicate business record",
                "raw_values": {k: str(v) for k, v in row_dict.items()}
            })
            continue
            
        seen_fingerprints.add(row_str_tuple)
        usable_rows.append({
            "source_file": filepath,
            "source_sheet": "work order tracker",
            "source_row_number": excel_row_num,
            "file_hash": file_hash,
            "raw_values": row_dict
        })
        
    metrics = {
        "dataset": "Work Orders",
        "file_hash": file_hash,
        "raw_worksheet_rows": total_raw_rows,
        "raw_worksheet_cols": total_raw_cols,
        "blank_rows_removed": blank_row_count,
        "repeated_header_rows_removed": 0,
        "duplicate_business_rows_removed": duplicate_count,
        "usable_business_records": len(usable_rows)
    }
    
    return usable_rows, rejected_rows, metrics
