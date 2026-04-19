from unittest.mock import patch
from movieapp.admin import AdminAuthMixin
from movieapp.models import UserRole


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
def test_admin_auth_mixin_inaccessible_callback_coverage(test_app):
    mixin = AdminAuthMixin()

    with test_app.test_request_context('/admin/bi-mat'):
        response = mixin.inaccessible_callback(name='test_view')

        # Kiểm tra xem có lệnh chuyển hướng (302) không
        assert response.status_code == 302

        # Kiểm tra xem có đúng là bị đá về trang chủ ('/') không
        assert response.location == '/'
