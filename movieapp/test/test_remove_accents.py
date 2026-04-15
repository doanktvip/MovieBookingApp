import pytest
from movieapp.dao import remove_accents

@pytest.mark.parametrize("input_data,expected_result",[
    ("", ""),
    (None, ""),
    ("Tiếng Việt", "tieng viet"),
    ("Đường Đi", "duong di"),
])
def test_remove_accents(input_data, expected_result):
    assert remove_accents(input_data) == expected_result