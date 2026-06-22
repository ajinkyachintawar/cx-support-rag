from src.retrieval.keyword import extract_policy_codes


def test_extract_single_code():
    codes = extract_policy_codes("What about REF-PREM-030?")
    assert "REF-PREM-030" in codes


def test_extract_multiple_codes():
    codes = extract_policy_codes("See VER-003 and SYS-4471 for details")
    assert "VER-003" in codes
    assert "SYS-4471" in codes


def test_extract_no_codes():
    codes = extract_policy_codes("What is the refund policy for standard customers?")
    assert codes == []


def test_extract_hyphenated_codes():
    codes = extract_policy_codes("Reference RET-SHIP-018")
    assert "RET-SHIP-018" in codes


def test_extract_case_insensitive():
    codes = extract_policy_codes("Check ref-prem-030 please")
    assert "REF-PREM-030" in codes
