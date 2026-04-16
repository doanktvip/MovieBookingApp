import pytest

from movieapp import dao
from movieapp.test.conftest import test_app, test_session, sample_users


def test_get_user_by_id(test_app, sample_users):
    u1 = sample_users["users"]["user1"]

    with test_app.app_context():
        # Trường hợp lấy u1 dựa vào id của u1
        user = dao.get_user_by_id(u1.id)
        assert user is not None
        assert user.id == u1.id
        assert user.username == "new_user1"

        # Trường hợp id không tồn tại trong database
        user_fail = dao.get_user_by_id(9999)
        assert user_fail is None


def test_get_user_by_username(test_app, sample_users):
    u1 = sample_users["users"]["user1"]

    with test_app.app_context():
        # Trường hợp lấy u1 dựa vào username của u1
        user = dao.get_user_by_username(u1.username)
        assert user is not None
        assert user.username == u1.username
        assert user.username == "new_user1"

        # Trường hợp username không tồn tại trong database
        user_fail = dao.get_user_by_username("user_khong_ton_tai")
        assert user_fail is None


def test_get_user_by_email(test_app, sample_users):
    u1 = sample_users["users"]["user1"]

    with test_app.app_context():
        # Trường hợp lấy u1 dựa vào email của u1
        user = dao.get_user_by_email(u1.email)
        assert user is not None
        assert user.email == u1.email
        assert user.email == "user1@gmail.com"

        # Trường hợp email không tồn tại trong database
        user_fail = dao.get_user_by_email("user_ao@gmail.com")
        assert user_fail is None


# HÀM AUTH_USER
# Trường hợp đăng nhập thành công
def test_auth_user_success(test_app, sample_users):
    with test_app.app_context():
        user = dao.auth_user(username="new_user1", password="123456")
        assert user is not None
        assert user.username == "new_user1"


# Trường hợp đúng định dạng nhưng sai mật khẩu
def test_auth_user_wrong_password(test_app, sample_users):
    with test_app.app_context():
        user = dao.auth_user(username="new_user1", password="wrongpassword")
        assert user is None


# Trường hợp đúng định dạng nhưng user không tồn tại
def test_auth_user_not_found(test_app, sample_users):
    with test_app.app_context():
        user = dao.auth_user(username="valid_user", password="validpassword")
        assert user is None


# Trường hợp thiếu dữ liệu
@pytest.mark.parametrize("username, password", [
    (None, "123456"),  # Thiếu username
    ("new_user1", None),  # Thiếu password
    (None, None),  # Thiếu cả hai
], ids=["missing_username", "missing_password", "missing_all"])
def test_auth_user_missing_fields(username, password, test_app):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Vui lòng nhập đầy đủ thông tin!"):
            dao.auth_user(username=username, password=password)


# Trường hợp username định dạng sai
@pytest.mark.parametrize("username", [
    "new user",  # Chứa khoảng trắng
    "người_dùng",  # Chứa tiếng Việt có dấu
    "user@123"  # Chứa ký tự đặc biệt (ngoài _)
], ids=["has_space", "has_vietnamese", "has_special_chars"])
def test_auth_user_invalid_username_format(username, test_app):
    with test_app.app_context():
        with pytest.raises(ValueError,
                           match="Tên đăng nhập chỉ được chứa chữ cái không dấu, số và '_', không có khoảng trắng!"):
            dao.auth_user(username=username, password=123456)


# Trường hợp password định dạng sai
@pytest.mark.parametrize("password", [
    "123 456",  # Chứa khoảng trắng
    "mậtkhẩu123"  # Chứa tiếng Việt có dấu
], ids=["pass_has_space", "pass_has_vietnamese"])
def test_auth_user_invalid_password_format(password, test_app):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Mật khẩu không được dùng tiếng Việt hoặc khoảng trắng!"):
            dao.auth_user(username="new_user1", password=password)


@pytest.mark.parametrize("username, password", [
    ("user", "123456"),  # Username quá ngắn (< 6 ký tự)
    ("a" * 51, "123456"),  # Username quá dài (> 50 ký tự)
    ("new_user1", "123"),  # Password quá ngắn (< 6 ký tự)
    ("new_user1", "a" * 51),  # Password quá dài (> 50 ký tự)
], ids=["user_too_short", "user_too_long", "pass_too_short", "pass_too_long"])
# Trường hợp sai độ dài
def test_auth_user_invalid_length(username, password, test_app):
    with test_app.app_context():
        with pytest.raises(ValueError, match="Tên đăng nhập và mật khẩu phải từ 6 đến 50 ký tự!"):
            dao.auth_user(username=username, password=password)
