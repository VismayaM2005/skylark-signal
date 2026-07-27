import sys, os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from skylark_signal.utils.text import clean_text, normalize_customer_code, map_category

def test_clean_text():
    assert clean_text("  hello   world  ") == "hello world"
    assert clean_text(None) is None
    assert clean_text("nan") is None
    assert clean_text("  ") is None

def test_customer_code_normalization():
    # Standard COMPANY005 -> COMPANY_005
    code, flag, sev, warn = normalize_customer_code("COMPANY005")
    assert code == "COMPANY_005"
    assert flag == "customer_code_normalized"
    assert sev == "info"

    # Standard COMPANY_005 -> COMPANY_005
    code, flag, sev, warn = normalize_customer_code("COMPANY_005")
    assert code == "COMPANY_005"
    assert flag == "customer_code_normalized"
    assert sev == "info"

    # WOCOMPANY_005 -> COMPANY_005
    code, flag, sev, warn = normalize_customer_code("WOCOMPANY_005")
    assert code == "COMPANY_005"
    assert flag == "customer_code_normalized"
    assert sev == "info"

    # WOCOMPANY_02 -> COMPANY_002
    code, flag, sev, warn = normalize_customer_code("WOCOMPANY_02")
    assert code == "COMPANY_002"
    assert flag == "customer_code_fallback"
    assert sev == "info"

def test_malformed_customer_code():
    code, flag, sev, warn = normalize_customer_code("CLIENT_ABC_99")
    assert code == "COMPANY_099"
    assert flag == "malformed_customer_code"
    assert sev == "warning"
    assert "Malformed" in warn

    code_inv, flag_inv, sev_inv, warn_inv = normalize_customer_code("NO_NUMBERS_HERE")
    assert flag_inv == "malformed_customer_code"
    assert sev_inv == "warning"

def test_map_category():
    mapping = {
        "Mining": "Mining",
        "Renewables": "Renewables",
        "A. Lead Generated": {"canonical_stage": "Lead Generated"}
    }
    cat, mapped, _ = map_category("Mining", mapping)
    assert cat == "Mining"
    assert mapped is True

    cat_case, mapped_case, _ = map_category("mining", mapping)
    assert cat_case == "Mining"
    assert mapped_case is True

    cat_stage, mapped_stage, _ = map_category("A. Lead Generated", mapping)
    assert cat_stage == "Lead Generated"
    assert mapped_stage is True

    cat_unknown, mapped_unknown, _ = map_category("Cybernetics", mapping)
    assert cat_unknown == "Cybernetics"
    assert mapped_unknown is False
