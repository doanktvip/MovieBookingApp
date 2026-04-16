from unittest.mock import patch
from movieapp import decorators
from movieapp.models import UserRole


# Tạo một hàm giả lập để áp dụng decorator vào
def mock_view():
    return "Success"


# Test login_user_required
def test_login_user_required_authenticated():
    # Giả lập người dùng ĐÃ đăng nhập
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.is_authenticated = True
        decorated = decorators.login_user_required(mock_view)
        result = decorated()
        assert result == "Success"


def test_login_user_required_unauthenticated():
    # Giả lập người dùng CHƯA đăng nhập
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.is_authenticated = False
        decorated = decorators.login_user_required(mock_view)
        result = decorated()
        # Phải chuyển hướng về trang chủ
        assert result.location == "/"


# Test anonymous_required
def test_anonymous_required_authenticated():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.is_authenticated = True
        decorated = decorators.anonymous_required(mock_view)
        result = decorated()
        assert result.location == "/"


def test_anonymous_required_unauthenticated():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.is_authenticated = False
        decorated = decorators.anonymous_required(mock_view)
        result = decorated()
        assert result == "Success"


# Test staff_required
def test_staff_required_success():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.role = UserRole.STAFF
        decorated = decorators.staff_required(mock_view)
        assert decorated() == "Success"


def test_staff_required_fail():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.role = UserRole.USER  # Không phải STAFF
        decorated = decorators.staff_required(mock_view)
        assert decorated().location == "/"


# Test user_required
def test_user_required_success():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.role = UserRole.USER
        decorated = decorators.user_required(mock_view)
        assert decorated() == "Success"


def test_user_required_fail():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.role = UserRole.ADMIN
        decorated = decorators.user_required(mock_view)
        assert decorated().location == "/"


# Test admin_required
def test_admin_required_success():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.role = UserRole.ADMIN
        decorated = decorators.admin_required(mock_view)
        assert decorated() == "Success"


def test_admin_required_fail():
    with patch('movieapp.decorators.current_user') as mock_user:
        mock_user.role = UserRole.STAFF
        decorated = decorators.admin_required(mock_view)
        assert decorated().location == "/"
