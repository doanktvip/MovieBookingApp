import pytest
from movieapp.test.conftest import test_client, test_app, test_session, sample_users


# TEST ĐĂNG KÝ THÀNH CÔNG
def test_register_api_success(test_client):
    res = test_client.post("/api/register", json={
        "username": "tester_new",
        "email": "tester_new@gmail.com",
        "password": "password123",
        "confirm_password": "password123"
    })

    assert res.status_code == 201
    data = res.get_json()
    assert data['status'] == "success"
    assert data['message'] == "Đăng ký tài khoản thành công."


# MẬT KHẨU XÁC NHẬN KHÔNG KHỚP
def test_register_api_fail_password_mismatch(test_client):
    res = test_client.post("/api/register", json={
        "username": "tester",
        "email": "test@gmail.com",
        "password": "123456",
        "confirm_password": "wrong_password"
    })

    assert res.status_code == 400
    assert res.get_json()['message'] == "Mật khẩu xác nhận không khớp!"


# THIẾU DỮ LIỆU
@pytest.mark.parametrize("payload", [
    {},  # Thiếu tất cả
    {"email": "test@gmail.com", "password": "123", "confirm_password": "123"},  # Thiếu username
    {"username": "tester", "password": "123", "confirm_password": "123"},  # Thiếu email
    {"username": "tester", "email": "test@gmail.com", "confirm_password": "123"},  # Thiếu password
    {"username": "tester", "email": "test@gmail.com", "password": "123"},  # Thiếu confirm_password
], ids=["missing_all", "missing_username", "missing_email", "missing_password", "missing_confirm"])
def test_register_api_fail_missing_data(test_client, payload):
    res = test_client.post("/api/register", json=payload)

    assert res.status_code == 400
    assert res.get_json()['message'] == "Vui lòng nhập đầy đủ thông tin!"


# SAI ĐỊNH DẠNG
@pytest.mark.parametrize("payload", [
    {"username": "nguoi dung", "email": "test@gmail.com", "password": "123456", "confirm_password": "123456"},
    {"username": "người_dùng", "email": "test@gmail.com", "password": "123456", "confirm_password": "123456"},
], ids=["username_has_space", "username_has_vietnamese"])
def test_register_api_fail_invalid_format(test_client, payload):
    res = test_client.post("/api/register", json=payload)

    assert res.status_code == 400
    assert res.get_json()[
               'message'] == "Tên đăng nhập chỉ được chứa chữ cái không dấu, số và '_', không có khoảng trắng!"


# ĐỘ DÀI (< 6 HOẶC > 50 KÝ TỰ)
@pytest.mark.parametrize("payload", [
    {"username": "user", "email": "new@gmail.com", "password": "123456", "confirm_password": "123456"},
    {"username": "valid_user", "email": "new@gmail.com", "password": "123", "confirm_password": "123"},
    {"username": "a" * 51, "email": "new@gmail.com", "password": "123456", "confirm_password": "123456"},
    {"username": "valid_user", "email": "new@gmail.com", "password": "a" * 51, "confirm_password": "a" * 51},
], ids=["username_too_short", "password_too_short", "username_too_long", "password_too_long"])
def test_register_api_fail_invalid_length(test_client, payload):
    res = test_client.post("/api/register", json=payload)

    assert res.status_code == 400
    assert res.get_json()['message'] == "Tên đăng nhập và mật khẩu phải từ 6 đến 50 ký tự!"


# TRÙNG LẶP DỮ LIỆU DB
@pytest.mark.parametrize("payload, expected_message", [
    ({"username": "new_user1", "email": "unique@gmail.com", "password": "123456", "confirm_password": "123456"},
     "Tên đăng nhập đã tồn tại!"),
    ({"username": "unique_user", "email": "user1@gmail.com", "password": "123456", "confirm_password": "123456"},
     "Email đã được sử dụng!"),
], ids=["duplicate_username", "duplicate_email"])
def test_register_api_fail_duplicates(test_client, sample_users, payload, expected_message):
    res = test_client.post("/api/register", json=payload)

    assert res.status_code == 400
    data = res.get_json()
    assert data is not None
    assert data.get('message') == expected_message
