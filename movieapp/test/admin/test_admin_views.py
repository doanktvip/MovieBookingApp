from unittest.mock import patch
from movieapp.admin import MyAdminIndexView
from movieapp.models import UserRole


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
def test_exit_view_redirect(test_client, sample_users):
    user = sample_users["users"]["user1"]

    # Giả lập đã đăng nhập để pass qua is_accessible
    with patch('flask_login.utils._get_user') as mocked_user:
        mocked_user.return_value = user

        # Truy cập vào endpoint của view (thường là /admin/exitview/)
        response = test_client.get('/admin/myexitview/')

        # Kiểm tra mã chuyển hướng 302 về trang chủ
        assert response.status_code == 302
        assert response.location == "/"
