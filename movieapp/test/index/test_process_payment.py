from datetime import datetime, timedelta

import pytest
from unittest.mock import patch


# --- TEST 1: KHÔNG CÓ GIỎ HÀNG (LỖI 404) ---
def test_process_payment_no_booking_session(test_client):
    response = test_client.post('/process_payment', data={'showtime_id': 1})

    # Khẳng định bị chặn lại bởi abort(404)
    assert response.status_code == 404

# --- TEST 2: HẾT HẠN GIỮ GHẾ (VỀ TRANG CHỦ) ---
@patch('movieapp.index.dao.get_reservation_expiry_time')
def test_process_payment_expired(mock_expiry, test_client, sample_users):
    # Ép thời gian hết hạn là 5 phút trong quá khứ
    mock_expiry.return_value = datetime.now() - timedelta(minutes=5)

    valid_user_id = str(sample_users["users"]["user1"].id)

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['booking'] = {'seat_1': {'price': 50000}}
        sess['user_session_id'] = 'session_123'

    response = test_client.post('/process_payment', data={'showtime_id': 1})

    # Bị flash lỗi và văng về trang chủ '/'
    assert response.status_code == 302
    assert response.location == '/'

# ---Các trường hợp khi if thỏa
# --- TEST 3: LỖI KHI TẠO BOOKING VÀO DATABASE ---
@patch('movieapp.index.dao.create_pending_booking')
@patch('movieapp.index.utils.stats_seats')
@patch('movieapp.index.dao.get_reservation_expiry_time')
def test_process_payment_create_db_error(mock_expiry, mock_stats, mock_create_db, test_client, sample_users):
    mock_expiry.return_value = datetime.now() + timedelta(minutes=10)
    mock_stats.return_value = {'total_amount': 50000, 'count': 1}

    # Ép hàm tạo DB văng lỗi giả lập
    mock_create_db.side_effect = Exception("Lỗi hệ thống khi tạo đơn hàng, vui lòng thử lại!")

    valid_user_id = str(sample_users["users"]["user1"].id)

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['booking'] = {'seat_1': {'price': 50000}}

    response = test_client.post('/process_payment', data={'showtime_id': 1})

    # Bị văng ngược lại trang checkout để thử lại
    assert response.status_code == 302
    assert '/checkout' in response.location


# --- TEST 4: GỌI MOMO THÀNH CÔNG (TRẢ VỀ PAYURL) ---
@patch('movieapp.index.create_momo_payment')
@patch('movieapp.index.dao.create_pending_booking')
@patch('movieapp.index.utils.stats_seats')
@patch('movieapp.index.dao.get_reservation_expiry_time')
def test_process_payment_momo_success(mock_expiry, mock_stats, mock_create_db, mock_momo, test_client, sample_users):
    mock_expiry.return_value = datetime.now() + timedelta(minutes=10)
    mock_stats.return_value = {'total_amount': 50000, 'count': 1}
    mock_create_db.return_value = 999  # Giả lập tạo thành công ID booking là 999

    # Giả lập MoMo trả về cục JSON có chứa 'payUrl'
    fake_pay_url = "https://test.momo.vn/pay/12345"
    mock_momo.return_value = {'payUrl': fake_pay_url}

    valid_user_id = str(sample_users["users"]["user1"].id)

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['booking'] = {'seat_1': {'price': 50000}}

    response = test_client.post('/process_payment', data={
        'showtime_id': 1,
        'payment_method': 'momo'
    })

    # Hệ thống phải chuyển hướng người dùng trực tiếp sang link của MoMo
    assert response.status_code == 302
    assert response.location == fake_pay_url

    # Kiểm tra thêm: Hệ thống có lưu đúng thông tin customer_info vào Session không?
    with test_client.session_transaction() as sess:
        assert 'customer_info' in sess
        assert sess['customer_info']['booking_id'] == 999
        assert sess['customer_info']['total_amount'] == 50000

# --- TEST 5: GỌI MOMO THẤT BẠI (KHÔNG CÓ PAYURL) ---
@patch('movieapp.index.create_momo_payment')
@patch('movieapp.index.dao.create_pending_booking')
@patch('movieapp.index.utils.stats_seats')
@patch('movieapp.index.dao.get_reservation_expiry_time')
def test_process_payment_momo_fail(mock_expiry, mock_stats, mock_create_db, mock_momo, test_client, sample_users):
    mock_expiry.return_value = datetime.now() + timedelta(minutes=10)
    mock_stats.return_value = {'total_amount': 50000, 'count': 1}
    mock_create_db.return_value = 999

    # Giả lập MoMo trả về lỗi (Không có key payUrl)
    mock_momo.return_value = {'message': 'Sai thông tin cấu hình', 'resultCode': 99}

    valid_user_id = str(sample_users["users"]["user1"].id)

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['booking'] = {'seat_1': {'price': 50000}}

    response = test_client.post('/process_payment', data={
        'showtime_id': 1,
        'payment_method': 'momo'
    })

    # Bị đá về trang checkout để chọn phương thức khác
    assert response.status_code == 302
    assert '/checkout' in response.location


# --- TEST 6: PHƯƠNG THỨC THANH TOÁN KHÁC ---
@patch('movieapp.index.dao.create_pending_booking')
@patch('movieapp.index.utils.stats_seats')
@patch('movieapp.index.dao.get_reservation_expiry_time')
def test_process_payment_other_method(mock_expiry, mock_stats, mock_create_db, test_client, sample_users):
    mock_expiry.return_value = datetime.now() + timedelta(minutes=10)
    mock_stats.return_value = {'total_amount': 50000, 'count': 1}
    mock_create_db.return_value = 999

    valid_user_id = str(sample_users["users"]["user1"].id)

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['booking'] = {'seat_1': {'price': 50000}}

    # Khách hàng chọn phương thức 'zalopay'
    response = test_client.post('/process_payment', data={
        'showtime_id': 1,
        'payment_method': 'zalopay'
    })

    # Trả về câu thông báo dạng chuỗi (Status Code mặc định là 200)
    assert response.status_code == 200
    assert "Chức năng thanh toán khác đang cập nhật" in response.get_data(as_text=True)

