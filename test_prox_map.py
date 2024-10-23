import pytest
from patron_update import create_prox_map


def test_create_prox_map_valid_format(tmp_path):
    # Create a temporary CSV file with valid format
    csv_content = """Active Accounts with Prox IDs
List of Active Accounts
"Universal ID","Student ID","Prox ID","Last Name","First Name","End Date","IsInactive"
"001000001","","000057426","Doe","John","12/12/2050","False"
"001000002","","000057427","Smith","Jane","12/12/2050","False"
"""
    csv_file = tmp_path / "prox.csv"
    csv_file.write_text(csv_content)

    # Call the function and check the result
    result = create_prox_map(csv_file)
    expected = {
        "1000001": "57426",
        "1000002": "57427",
    }
    assert result == expected


def test_create_prox_map_invalid_format(tmp_path):
    # Create a temporary CSV file with invalid format
    csv_content = """Invalid Header
"Universal ID","Student ID","Prox ID","Last Name","First Name","End Date","IsInactive"
"001000001","","000057426","Doe","John","12/12/2050","False"
"""
    csv_file = tmp_path / "prox.csv"
    csv_file.write_text(csv_content)

    # Call the function and check for RuntimeError
    with pytest.raises(RuntimeError):
        create_prox_map(csv_file)


def test_create_prox_map_empty_prox(tmp_path):
    # Create a temporary CSV file with empty prox IDs
    csv_content = """Active Accounts with Prox IDs
List of Active Accounts
"Universal ID","Student ID","Prox ID","Last Name","First Name","End Date","IsInactive"
"001000001","","","Doe","John","12/12/2050","False"
"001000002","","000000000","Smith","Jane","12/12/2050","False"
"""
    csv_file = tmp_path / "prox.csv"
    csv_file.write_text(csv_content)

    # Call the function and check the result
    result = create_prox_map(csv_file)
    expected = {}
    assert result == expected


def test_create_prox_map_leading_zeroes(tmp_path):
    # Create a temporary CSV file with leading zeroes in prox IDs
    csv_content = """Active Accounts with Prox IDs
List of Active Accounts
"Universal ID","Student ID","Prox ID","Last Name","First Name","End Date","IsInactive"
"001000001","","000057426","Doe","John","12/12/2050","False"
"001000002","","000057427","Smith","Jane","12/12/2050","False"
"""
    csv_file = tmp_path / "prox.csv"
    csv_file.write_text(csv_content)

    # Call the function and check the result
    result = create_prox_map(csv_file)
    expected = {
        "1000001": "57426",
        "1000002": "57427",
    }
    assert result == expected
