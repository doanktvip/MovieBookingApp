from unittest.mock import patch
from movieapp.admin import MyAdminIndexView, MyLogoutView
from movieapp.models import UserRole  # Đừng quên import UserRole


# TEST: index (MyAdminIndexView)
@patch('movieapp.admin.current_user')
@patch('movieapp.admin.User.query')
@patch('movieapp.admin.Movie.query')
@patch('movieapp.admin.Booking.query')
@patch.object(MyAdminIndexView, 'render')
def test_my_admin_index_view_coverage(mock_render, mock_booking, mock_movie, mock_user, mock_current_user, test_app):
    # CẤP QUYỀN: Giả lập có Admin đang đăng nhập để không bị đá ra ngoài
    mock_current_user.is_authenticated = True
    mock_current_user.role = UserRole.ADMIN

    # Giả lập số liệu trả về từ Database
    mock_user.count.return_value = 50
    mock_movie.filter_by.return_value.count.return_value = 12
    mock_booking.count.return_value = 150

    view = MyAdminIndexView()

    # Bắt buộc phải có request context
    with test_app.test_request_context('/admin/'):
        view.index()

        # Đảm bảo hàm render template được gọi 1 lần
        mock_render.assert_called_once()

        # 3. Lấy các tham số đã truyền vào hàm render để kiểm tra
        args, kwargs = mock_render.call_args

        assert 'stats' in kwargs
        stats = kwargs['stats']

        # Kiểm tra xem các con số đếm có chuẩn không
        assert stats['users'] == 50
        assert stats['movies'] == 12
        assert stats['bookings'] == 150


# TEST: index (MyLogoutView)
@patch('movieapp.admin.current_user')
@patch('movieapp.admin.logout_user')
def test_my_logout_view_index_coverage(mock_logout, mock_user, test_app):
    # Cấp quyền: Giả lập người dùng đang đăng nhập
    mock_user.is_authenticated = True

    view = MyLogoutView()

    # Cần request context để hàm redirect() hoạt động trơn tru
    with test_app.test_request_context('/admin/logout/'):
        response = view.index()

        # Kiểm tra xem dòng 352 (logout_user) có được thực thi không
        mock_logout.assert_called_once()

        # Kiểm tra xem dòng 353 có trả về lệnh chuyển hướng (302) về trang chủ "/" không
        assert response.status_code == 302
        assert response.location == '/'


# TEST: is_accessible (MyLogoutView)
@patch('movieapp.admin.current_user')
def test_my_logout_view_is_accessible_coverage(mock_user):
    view = MyLogoutView()

    # Trường hợp 1: Người dùng đã đăng nhập -> Trả về True
    mock_user.is_authenticated = True
    assert view.is_accessible() is True

    # Trường hợp 2: Người dùng chưa đăng nhập -> Trả về False
    mock_user.is_authenticated = False
    assert view.is_accessible() is False
