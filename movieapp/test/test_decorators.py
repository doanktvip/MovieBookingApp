import pytest
from unittest.mock import patch
from werkzeug.exceptions import Unauthorized, Forbidden
from movieapp import decorators
from movieapp.models import UserRole


# Tạo một hàm giả lập để áp dụng decorator vào
def mock_view():
    return "Success"


# --- TEST login_user_required ---
@patch('movieapp.decorators.current_user')
def test_login_user_required_authenticated(mock_user):
    mock_user.is_authenticated = True
    decorated = decorators.login_user_required(mock_view)
    assert decorated() == "Success"


@patch('movieapp.decorators.current_user')
def test_login_user_required_unauthenticated(mock_user):
    mock_user.is_authenticated = False
    decorated = decorators.login_user_required(mock_view)
    # Kiểm tra xem có văng lỗi 401 không
    with pytest.raises(Unauthorized) as excinfo:
        decorated()
    assert excinfo.value.code == 401


# --- TEST anonymous_required ---
@patch('movieapp.decorators.current_user')
def test_anonymous_required_authenticated(mock_user):
    mock_user.is_authenticated = True
    decorated = decorators.anonymous_required(mock_view)
    # Đã đăng nhập mà vào trang ẩn danh -> 403
    with pytest.raises(Forbidden) as excinfo:
        decorated()
    assert excinfo.value.code == 403


@patch('movieapp.decorators.current_user')
def test_anonymous_required_unauthenticated(mock_user):
    mock_user.is_authenticated = False
    decorated = decorators.anonymous_required(mock_view)
    assert decorated() == "Success"


# --- TEST staff_or_admin_required ---
@patch('movieapp.decorators.current_user')
def test_staff_or_admin_required_success_staff(mock_user):
    mock_user.is_authenticated = True
    mock_user.role = UserRole.STAFF
    decorated = decorators.staff_or_admin_required(mock_view)
    assert decorated() == "Success"


@patch('movieapp.decorators.current_user')
def test_staff_or_admin_required_success_admin(mock_user):
    mock_user.is_authenticated = True
    mock_user.role = UserRole.ADMIN
    decorated = decorators.staff_or_admin_required(mock_view)
    assert decorated() == "Success"


@patch('movieapp.decorators.current_user')
def test_staff_or_admin_required_fail_user(mock_user):
    mock_user.is_authenticated = True
    mock_user.role = UserRole.USER
    decorated = decorators.staff_or_admin_required(mock_view)
    with pytest.raises(Forbidden) as excinfo:
        decorated()
    assert excinfo.value.code == 403


# --- TEST user_required ---
@patch('movieapp.decorators.current_user')
def test_user_required_success(mock_user):
    mock_user.is_authenticated = True
    mock_user.role = UserRole.USER
    decorated = decorators.user_required(mock_view)
    assert decorated() == "Success"


@patch('movieapp.decorators.current_user')
def test_user_required_fail_admin(mock_user):
    mock_user.is_authenticated = True
    mock_user.role = UserRole.ADMIN
    decorated = decorators.user_required(mock_view)
    with pytest.raises(Forbidden) as excinfo:
        decorated()
    assert excinfo.value.code == 403


@patch('movieapp.decorators.current_user')
def test_staff_or_admin_required_unauthenticated(mock_user):
    mock_user.is_authenticated = False

    decorated = decorators.staff_or_admin_required(mock_view)

    with pytest.raises(Unauthorized) as excinfo:
        decorated()

    assert excinfo.value.code == 401
