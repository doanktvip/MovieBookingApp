from unittest.mock import patch
import pytest
from movieapp import dao
from movieapp.test.conftest import test_app, test_session, sample_users


# TEST TRƯỜNG HỢP THÀNH CÔNG
def test_add_user_success(test_app, test_session):
    with test_app.app_context():
        u = dao.add_user(username="new_user_123", email="newuser@gmail.com", password="password123")
        assert u is not None
        assert u.username == "new_user_123"
        assert u.id is not None


# TEST LỖI THIẾU THÔNG TIN (TRỐNG HOẶC NONE)
@pytest.mark.parametrize("username, email, password", [
    (None, "test@gmail.com", "123456"),  # Thiếu username
    ("user123", None, "123456"),  # Thiếu email
    ("user123", "test@gmail.com", None),  # Thiếu password
    (None, None, "123456"),  # Thiếu username, email
    ("user123", None, None),  # Thiếu email, password
    (None, "test@gmail.com", None),  # Thiếu username, password
    (None, None, None),  # Thiếu cả 3
], ids=["missing_username", "missing_email", "missing_password", "missing_user_and_email", "missing_email_and_pass",
        "missing_user_and_pass", "missing_all"])
def test_add_user_fail_missing_info(test_app, username, email, password):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin!"):
            dao.add_user(username=username, email=email, password=password)


# TEST LỖI SAI ĐỊNH DẠNG USERNAME
@pytest.mark.parametrize("invalid_username", [
    "user name",  # Có khoảng trắng
    "người_dùng",  # Tiếng Việt có dấu
    "user@123",  # Ký tự đặc biệt (ngoài _)
], ids=["space_in_username", "vietnamese_in_username", "special_chars_in_username"])
def test_add_user_fail_username_format(test_app, invalid_username):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Tên đăng nhập chỉ được chứa chữ cái không dấu.*"):
            dao.add_user(username=invalid_username, email="test@gmail.com", password="password123")


# TEST LỖI SAI ĐỊNH DẠNG EMAIL & PASSWORD
@pytest.mark.parametrize("invalid_email", [
    "test email@gmail.com",  # Chứa khoảng trắng
    "email_có_dấu@gmail.com"  # Chứa tiếng Việt có dấu
], ids=["space_in_email", "vietnamese_in_email"])
def test_add_user_fail_email_format(test_app, invalid_email):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Email không được dùng tiếng Việt hoặc khoảng trắng!"):
            dao.add_user(username="valid_user", email=invalid_email, password="password123")


@pytest.mark.parametrize("invalid_password", [
    "pass word",  # Chứa khoảng trắng
    "mậtkhẩu123"  # Chứa tiếng Việt có dấu
], ids=["space_in_password", "vietnamese_in_password"])
def test_add_user_fail_password_format(test_app, invalid_password):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Mật khẩu không được dùng tiếng Việt hoặc khoảng trắng!"):
            dao.add_user(username="valid_user", email="test@gmail.com", password=invalid_password)


# TEST LỖI VƯỢT QUÁ ĐỘ DÀI CHO PHÉP
@pytest.mark.parametrize("username, password", [
    ("user", "123456"),  # Username quá ngắn (< 6 ký tự)
    ("a" * 51, "123456"),  # Username quá dài (> 50 ký tự)
    ("new_user1", "123"),  # Password quá ngắn (< 6 ký tự)
    ("new_user1", "a" * 51),  # Password quá dài (> 50 ký tự)
], ids=["username_too_short", "username_too_long", "password_too_short", "password_too_long"])
def test_add_user_fail_invalid_length(test_app, username, password):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Tên đăng nhập và mật khẩu phải từ 6 đến 50 ký tự!"):
            dao.add_user(username=username, email="test@gmail.com", password=password)


# TEST LỖI TRÙNG LẶP DỮ LIỆU (DUPLICATE)
def test_add_user_fail_duplicate_username(test_app, sample_users):
    u1 = sample_users["users"]["user1"]
    with test_app.app_context():
        with pytest.raises(ValueError, match="Tên đăng nhập đã tồn tại!"):
            dao.add_user(username=u1.username, email="unique@gmail.com", password="password123")


def test_add_user_fail_duplicate_email(test_app, sample_users):
    u1 = sample_users["users"]["user1"]
    with test_app.app_context():
        with pytest.raises(ValueError, match="Email đã được sử dụng!"):
            dao.add_user(username="unique_user", email=u1.email, password="password123")


# TEST LỖI HỆ THỐNG (Khối try...except)
def test_add_user_fail_system_error(test_app):
    with test_app.app_context():
        # Dùng 'patch' để giả lập lỗi khi DB thực hiện commit
        with patch('movieapp.db.session.commit', side_effect=Exception("Lỗi DB giả lập")):
            with pytest.raises(ValueError, match="Đã xảy ra lỗi hệ thống khi lưu dữ liệu!"):
                dao.add_user(username="valid_user", email="valid@gmail.com", password="password123")
