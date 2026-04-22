from unittest.mock import patch, MagicMock
from movieapp.models import BookingStatus, UserRole


# Tạo sẵn một user giả để dùng chung cho các test bên dưới
def get_mock_user():
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.role = UserRole.USER
    mock_user.id = 1
    return mock_user


# --- TEST 1: KHÔNG CÓ THÔNG TIN KHÁCH HÀNG (SESSION BỊ MẤT) ---
def test_momo_return_no_customer_info(test_client):
    mock_user = get_mock_user()

    # Vượt ải đăng nhập
    with patch('movieapp.decorators.current_user', mock_user):
        # Gửi GET request có kèm tham số nhưng KHÔNG giả lập Session
        response = test_client.get('/momo_return?resultCode=0&orderId=123')

        # Bị bắt lỗi và đá về trang chủ
        assert response.status_code == 302
        assert response.location == '/'


# --- TEST 2: THANH TOÁN THÀNH CÔNG (RESULT CODE = '0') ---
@patch('movieapp.index.dao.clear_db_booking_by_session')
@patch('movieapp.index.dao.update_status_booking')
def test_momo_return_success(mock_update_status, mock_clear_db, test_client):
    mock_user = get_mock_user()

    with test_client.session_transaction() as sess:
        sess['customer_info'] = {'booking_id': 999}
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}}

    with patch('movieapp.decorators.current_user', mock_user):
        response = test_client.get('/momo_return?resultCode=0&orderId=MOMO123&message=Success')

        assert response.status_code == 302
        assert response.location == '/'

        mock_update_status.assert_called_once_with(999, BookingStatus.PAID, 'session_123')
        mock_clear_db.assert_called_once_with('session_123')

    with test_client.session_transaction() as sess:
        assert 'booking' not in sess
        assert 'customer_info' not in sess


# --- TEST 3: THANH TOÁN THÀNH CÔNG NHƯNG DATABASE BỊ LỖI ---
@patch('movieapp.index.dao.update_status_booking')
def test_momo_return_db_exception(mock_update_status, test_client):
    mock_user = get_mock_user()

    mock_update_status.side_effect = [Exception("Lỗi mất kết nối CSDL"), None]

    with test_client.session_transaction() as sess:
        sess['customer_info'] = {'booking_id': 999}
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}}

    with patch('movieapp.decorators.current_user', mock_user):
        response = test_client.get('/momo_return?resultCode=0')

        assert response.status_code == 302
        assert response.location == '/'

        assert mock_update_status.call_count == 2
        mock_update_status.assert_any_call(999, BookingStatus.PAID, 'session_123')
        mock_update_status.assert_any_call(999, BookingStatus.FAILED, 'session_123')

    with test_client.session_transaction() as sess:
        assert 'booking' not in sess
        assert 'customer_info' in sess


# --- TEST 4: KHÁCH HỦY THANH TOÁN HOẶC LỖI (RESULT CODE KHÁC '0') ---
@patch('movieapp.index.dao.update_status_booking')
def test_momo_return_failed_or_cancelled(mock_update_status, test_client):
    mock_user = get_mock_user()

    with test_client.session_transaction() as sess:
        sess['customer_info'] = {'booking_id': 999}
        sess['user_session_id'] = 'session_123'

    with patch('movieapp.decorators.current_user', mock_user):
        response = test_client.get('/momo_return?resultCode=1006&message=UserCancelled')

        assert response.status_code == 302
        assert response.location == '/'

        mock_update_status.assert_called_once_with(999, BookingStatus.PENDING, 'session_123')
