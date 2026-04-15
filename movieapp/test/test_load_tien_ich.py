from unittest.mock import Mock, patch, mock_open

import pytest

from movieapp.dao import load_tien_ich


@patch('builtins.open', mock_open(read_data='{"wifi": true}'))
def test_load_success():
    assert load_tien_ich() == {"wifi": True}

def test_load_failed():
    with patch('builtins.open') as mock_json:
        mock_json.side_effect=Exception('FileNotFoundError')
        with pytest.raises(Exception):
            load_tien_ich()
def test_load_error_format_file():
    with patch('builtins.open',mock_open(read_data="{wifi: true, error]")) as mock_json:
        mock_json.side_effect=Exception("Error Format Json File")
        with pytest.raises(Exception):
            load_tien_ich()