from unittest.mock import patch, mock_open
from movieapp.dao import load_tien_ich


# TRƯỜNG HỢP THÀNH CÔNG
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='[{"name": "Wifi", "icon": "fa-wifi"}]')
def test_load_tien_ich_success(mock_file, mock_exists):
    mock_exists.return_value = True

    result = load_tien_ich()

    assert isinstance(result, list)
    assert result[0]["name"] == "Wifi"
    mock_file.assert_called_once()
    assert mock_file.call_args.kwargs['encoding'] == 'utf-8'


# TRƯỜNG HỢP FILE KHÔNG TỒN TẠI
@patch('os.path.exists')
def test_load_tien_ich_file_not_found(mock_exists):
    mock_exists.return_value = False

    result = load_tien_ich()

    assert result == []
    with patch('builtins.open') as mock_file:
        load_tien_ich()
        mock_file.assert_not_called()


# TRƯỜNG HỢP FILE CÓ NHƯNG SAI ĐỊNH DẠNG JSON
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{ "error": "missing bracket" ')
def test_load_tien_ich_invalid_json(mock_file, mock_exists):
    mock_exists.return_value = True

    result = load_tien_ich()

    assert result == []


# TRƯỜNG HỢP LỖI HỆ THỐNG KHÔNG XÁC ĐỊNH
@patch('os.path.exists')
def test_load_tien_ich_system_exception(mock_exists):
    mock_exists.return_value = True
    with patch('builtins.open', side_effect=Exception("Unexpected Error")):
        result = load_tien_ich()
        assert result == []


# KIỂM TRA LOGIC ĐƯỜNG DẪN
@patch('os.path.abspath')
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='[]')
def test_load_tien_ich_correct_path(mock_file, mock_exists, mock_abs):
    mock_abs.return_value = "D:\\GitHub\\MovieBookingApp\\movieapp\\dao.py"
    mock_exists.return_value = True

    load_tien_ich()

    called_path = mock_file.call_args[0][0]

    assert "movieapp" in called_path
    assert "data" in called_path
    assert "tienich.json" in called_path
