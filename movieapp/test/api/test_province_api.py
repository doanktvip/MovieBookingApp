from unittest.mock import patch


# Test thêm tỉnh hợp lệ
def test_add_province_quick_success(test_client, test_session):
    res = test_client.post('/api/add_province_quick', json={'name': 'Đà Nẵng'})
    assert res.status_code == 200
    assert res.get_json()['name'] == 'Đà Nẵng'


# Test gửi tên tỉnh trống
def test_add_province_quick_empty_name(test_client):
    res = test_client.post('/api/add_province_quick', json={'name': '   '})
    assert res.status_code == 400
    assert res.get_json()['message'] == 'Tên không được để trống'


# Test xử lý khi có lỗi database
@patch('movieapp.dao.get_or_create_province')
def test_add_province_quick_exception(mock_get_or_create, test_client):
    mock_get_or_create.side_effect = Exception("Database crashed")
    res = test_client.post('/api/add_province_quick', json={'name': 'Lỗi Test'})
    assert res.status_code == 500
    assert 'Database crashed' in res.get_json()['message']
