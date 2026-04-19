from datetime import datetime, timedelta

import pytest
from unittest.mock import patch

from movieapp.models import BookingStatus


# --- TEST 1: KHÔNG CÓ THÔNG TIN KHÁCH HÀNG (SESSION BỊ MẤT) ---
def test_momo_return_no_customer_info(test_client):
    # Gửi GET request có kèm tham số nhưng KHÔNG giả lập Session
    response = test_client.get('/momo_return?resultCode=0&orderId=123')

    # Bị bắt lỗi và đá về trang chủ
    assert response.status_code == 302
    assert response.location == '/'


# --- TEST 2: THANH TOÁN THÀNH CÔNG (RESULT CODE = '0') ---
@patch('movieapp.index.dao.clear_db_booking_by_session')
@patch('movieapp.index.dao.update_status_booking')
def test_momo_return_success(mock_update_status, mock_clear_db, test_client):
    # 1. Giả lập Session (Có customer_info và booking)
    with test_client.session_transaction() as sess:
        sess['customer_info'] = {'booking_id': 999}
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}}

    # 2. Gửi request giả lập MoMo gọi về URL
    response = test_client.get('/momo_return?resultCode=0&orderId=MOMO123&message=Success')

    #Kiểm tratrả về trang chủ
    assert response.status_code == 302
    assert response.location == '/'

    # 3. Database được gọi 1 lần duy nhất đÚNG với trạng thái PAID (Đã thanh toán)
    mock_update_status.assert_called_once_with(999, BookingStatus.PAID, 'session_123')
    mock_clear_db.assert_called_once_with('session_123')

    # 4. Khẳng định Session đã được dọn dẹp sạch sẽ
    with test_client.session_transaction() as sess:
        assert 'booking' not in sess
        assert 'customer_info' not in sess


# --- TEST 3: THANH TOÁN THÀNH CÔNG NHƯNG DATABASE BỊ LỖI ---
@patch('movieapp.index.dao.update_status_booking')
def test_momo_return_db_exception(mock_update_status, test_client):
    #Lần gọi đầu tiên (PAID) văng lỗi, Lần gọi thứ 2 (FAILED) thành công
    mock_update_status.side_effect = [Exception("Lỗi mất kết nối CSDL"), None]

    with test_client.session_transaction() as sess:
        sess['customer_info'] = {'booking_id': 999}
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}}

    response = test_client.get('/momo_return?resultCode=0')

    assert response.status_code == 302
    assert response.location == '/'

    # Kiểm tra hàm update DB bị gọi 2 lần (1 lần cập nhật PAID thất bại, 1 lần cập nhật FAILED để cứu hộ)
    assert mock_update_status.call_count == 2
    mock_update_status.assert_any_call(999, BookingStatus.PAID, 'session_123')
    mock_update_status.assert_any_call(999, BookingStatus.FAILED, 'session_123')

    # Khẳng định giỏ hàng bị xóa nhưng customer_info thì VẪN CÒN
    with test_client.session_transaction() as sess:
        assert 'booking' not in sess
        assert 'customer_info' in sess


# --- TEST 4: KHÁCH HỦY THANH TOÁN HOẶC LỖI (RESULT CODE KHÁC '0') ---
@patch('movieapp.index.dao.update_status_booking')
def test_momo_return_failed_or_cancelled(mock_update_status, test_client):
    with test_client.session_transaction() as sess:
        sess['customer_info'] = {'booking_id': 999}
        sess['user_session_id'] = 'session_123'

    # Giả lập MoMo trả về mã lỗi 1006 (Khách hủy giao dịch)
    response = test_client.get('/momo_return?resultCode=1006&message=UserCancelled')

    assert response.status_code == 302
    assert response.location == '/'

    # Khẳng định Database cập nhật đơn hàng thành PENDING
    mock_update_status.assert_called_once_with(999, BookingStatus.PENDING, 'session_123')