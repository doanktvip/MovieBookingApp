import pytest
from movieapp.test.test_base import test_client, test_app, sample_users, test_session


# TEST ĐĂNG NHẬP THÀNH CÔNG
def test_api_login_success(test_client, sample_users):
    valid_user = sample_users["users"]["user1"]

    res = test_client.post("/api/login", json={
        "username": valid_user.username,
        "password": "123456"
    })

    assert res.status_code == 200

    data = res.get_json()
    assert data['status'] == "success"
    assert data['message'] == "Đăng nhập thành công"
    assert data['data']['username'] == valid_user.username
    assert data['data']['role'] in ["USER", "user"]


# SAI THÔNG TIN ĐĂNG NHẬP
@pytest.mark.parametrize("payload", [
    {"username": "new_user1", "password": "wrong_password"},  # Đúng user, sai pass
    {"username": "ghost_user", "password": "123456"},  # Sai user
], ids=["wrong_password", "user_not_found"])
def test_api_login_fail_wrong_credentials(test_client, sample_users, payload):
    res = test_client.post("/api/login", json=payload)

    assert res.status_code == 401
    assert res.get_json()['message'] == "Tên đăng nhập hoặc mật khẩu không đúng!"


# THIẾU DỮ LIỆU BẮT BUỘC
@pytest.mark.parametrize("payload", [
    {},  # Thiếu cả 2
    {"password": "123456"},  # Thiếu username
    {"username": "new_user1"},  # Thiếu password
], ids=["missing_all", "missing_username", "missing_password"])
def test_api_login_fail_missing_data(test_client, payload):
    res = test_client.post("/api/login", json=payload)

    assert res.status_code == 400
    assert res.get_json()['message'] == "Vui lòng nhập đầy đủ thông tin!"


# ĐỘ DÀI KHÔNG HỢP LỆ
@pytest.mark.parametrize("payload", [
    {"username": "abc", "password": "123456"},  # Username < 6 ký tự
    {"username": "new_user1", "password": "123"},  # Password < 6 ký tự
    {"username": "a" * 51, "password": "123456"},  # Username > 50 ký tự
    {"username": "new_user1", "password": "a" * 51}  # Password > 50 ký tự
], ids=["username_too_short", "password_too_short", "username_too_long", "password_too_long"])
def test_api_login_fail_invalid_length(test_client, payload):
    res = test_client.post("/api/login", json=payload)

    assert res.status_code == 400
    assert res.get_json()['message'] == "Tên đăng nhập và mật khẩu phải từ 6 đến 50 ký tự!"


# SAI ĐỊNH DẠNG USERNAME
@pytest.mark.parametrize("payload", [
    {"username": "new user", "password": "123456"},  # Chứa khoảng trắng
    {"username": "người_dùng", "password": "123456"},  # Chứa tiếng Việt có dấu
], ids=["username_contains_space", "username_contains_vietnamese"])
def test_api_login_fail_invalid_username_format(test_client, payload):
    res = test_client.post("/api/login", json=payload)

    assert res.status_code == 400
    assert res.get_json()[
               'message'] == "Tên đăng nhập chỉ được chứa chữ cái không dấu, số và '_', không có khoảng trắng!"


# SAI ĐỊNH DẠNG PASSWORD
@pytest.mark.parametrize("payload", [
    {"username": "new_user1", "password": "mật_khẩu"},  # Chứa tiếng Việt có dấu
    {"username": "new_user1", "password": "123 456"},  # Chứa khoảng trắng
], ids=["password_contains_vietnamese", "password_contains_space"])
def test_api_login_fail_invalid_password_format(test_client, payload):
    res = test_client.post("/api/login", json=payload)

    assert res.status_code == 400
    assert res.get_json()['message'] == "Mật khẩu không được dùng tiếng Việt hoặc khoảng trắng!"
