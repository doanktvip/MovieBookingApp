import pytest
from movieapp.admin import AdminAuthMixin
from movieapp.models import UserRole
from unittest.mock import patch
from werkzeug.exceptions import Unauthorized, Forbidden

# TEST: is_accessible
@patch('movieapp.admin.current_user')
def test_admin_auth_mixin_is_accessible_coverage(mock_user):
    mixin = AdminAuthMixin()

    # Nhánh 1: Khách vãng lai (Chưa đăng nhập) -> Sai ngay từ vế đầu
    mock_user.is_authenticated = False
    assert mixin.is_accessible() is False

    # Nhánh 2: Đã đăng nhập nhưng là User thường -> Sai ở vế sau
    mock_user.is_authenticated = True
    mock_user.role = UserRole.USER
    assert mixin.is_accessible() is False

    # Nhánh 3: Đã đăng nhập và là ADMIN -> Đúng cả 2 vế
    mock_user.role = UserRole.ADMIN
    assert mixin.is_accessible() is True


# TEST: inaccessible_callback
@patch('movieapp.admin.current_user')
def test_admin_auth_mixin_inaccessible_callback_coverage(mock_user, test_app):
    mixin = AdminAuthMixin()

    with test_app.test_request_context('/admin/bi-mat'):
        # Nhánh 1: Chưa đăng nhập -> abort(401) sẽ ném ra lỗi Unauthorized
        mock_user.is_authenticated = False
        with pytest.raises(Unauthorized) as excinfo:
            mixin.inaccessible_callback(name='test_view')
        assert excinfo.value.code == 401

        # Nhánh 2: Đã đăng nhập nhưng không phải ADMIN -> abort(403) sẽ ném ra lỗi Forbidden
        mock_user.is_authenticated = True
        mock_user.role = UserRole.USER
        with pytest.raises(Forbidden) as excinfo:
            mixin.inaccessible_callback(name='test_view')
        assert excinfo.value.code == 403
