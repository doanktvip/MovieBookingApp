from datetime import datetime, timedelta

import pytest
from unittest.mock import patch

from movieapp.utils import slugify


# ---  LỖI 404 KHI KHÔNG TÌM THẤY SUẤT CHIẾU ---
@patch('movieapp.index.dao.get_showtime_by_id')
def test_checkout_showtime_not_found(mock_get_showtime,test_client,sample_users):
    # Ép DAO trả về None (không tìm thấy phim)
    mock_get_showtime.return_value = None

    valid_user_id = str(sample_users["users"]["user1"].id)

    # Giả lập User ĐÃ ĐĂNG NHẬP để vượt qua @login_user_required
    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id

    response = test_client.post('/checkout', data={'showtime_id': 9999})
    assert response.status_code == 404

#--- LỖI HẾT HẠN GIỮ GHẾ ---(#Khách có giỏ hàng, có expire_time nhưng hết hạn giữ ghế)
@patch('movieapp.index.dao.get_showtime_by_id')
@patch('movieapp.index.dao.get_reservation_expiry_time')
def test_checkout_expired_session(mock_expiry, mock_get_showtime, test_client, sample_showtimes_complex,sample_users):
    # Trích xuất dữ liệu rạp từ fixture để làm mồi
    st_mock = sample_showtimes_complex['showtime']
    mock_get_showtime.return_value = st_mock

    # Ép thời gian hết hạn là 5 phút TRƯỚC (đã hết hạn)
    mock_expiry.return_value = datetime.now() - timedelta(minutes=5)
    valid_user_id = str(sample_users["users"]["user1"].id)
    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}}

    response = test_client.post('/checkout', data={'showtime_id': st_mock.id})

    # Khẳng định hệ thống từ chối và chuyển hướng (Status code 302)
    assert response.status_code == 302

    expected_slug = slugify(st_mock.room.cinema.name)
    expected_url = f"/booking/showtime-{st_mock.id}-{expected_slug}-room-{st_mock.room_id}"

    # 2. Khẳng định URL chuyển hướng trả về khớp với URL mong muốn(response.location là trả về đường dẫn đích đến )
    assert expected_url in response.location

# Lỗi không có giỏ hàng( không có booking session
@patch('movieapp.index.dao.get_showtime_by_id')
def test_checkout_no_booking_session(mock_get_showtime, test_client, sample_showtimes_complex, sample_users):
    st_mock = sample_showtimes_complex['showtime']
    mock_get_showtime.return_value = st_mock
    valid_user_id = str(sample_users["users"]["user1"].id)

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {}

    response = test_client.post('/checkout', data={'showtime_id': st_mock.id})

    assert response.status_code == 302
    assert f"/booking/showtime-{st_mock.id}" in response.location

#Khách có giỏ hàng nhưng không tìm thấy expire_time
@patch('movieapp.index.dao.get_reservation_expiry_time')
@patch('movieapp.index.dao.get_showtime_by_id')
def test_checkout_no_expire_time(mock_get_showtime, mock_expiry, test_client, sample_showtimes_complex, sample_users):
    st_mock = sample_showtimes_complex['showtime']
    mock_get_showtime.return_value = st_mock
    valid_user_id = str(sample_users["users"]["user1"].id)

    # CỐ TÌNH ÉP DAO TRẢ VỀ NONE CHO EXPIRE_TIME
    mock_expiry.return_value = None

    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}}  # CÓ GIỎ HÀNG

    response = test_client.post('/checkout', data={'showtime_id': st_mock.id})

    assert response.status_code == 302
    assert f"/booking/showtime-{st_mock.id}" in response.location

#Trường hợp Success
@patch('movieapp.index.render_template')
@patch('movieapp.index.utils.stats_seats')
@patch('movieapp.index.dao.get_reservation_expiry_time')
@patch('movieapp.index.dao.get_showtime_by_id')
def test_checkout_success(mock_get_showtime, mock_expiry, mock_stats, mock_render, test_client,
                          sample_showtimes_complex, sample_users):

    # 1. Ép render_template trả về chuỗi ảo để khỏi báo lỗi TemplateNotFound
    mock_render.return_value = "Mocked HTML"

    st_mock = sample_showtimes_complex['showtime']
    mock_get_showtime.return_value = st_mock

    #  Ép thời gian hết hạn là 10 phút NỮA (Còn dư dả thời gian)
    mock_expiry.return_value = datetime.now() + timedelta(minutes=10)

    # Giả lập hàm tính tiền trả về giỏ hàng 150k
    mock_stats.return_value = {'total_amount': 150000, 'count': 2}

    # Lấy ID user thật trong DB ảo
    valid_user_id = str(sample_users["users"]["user1"].id)

    # 4. GIẢ LẬP ĐĂNG NHẬP VÀ CHỌN GHẾ
    with test_client.session_transaction() as sess:
        sess['_user_id'] = valid_user_id
        sess['user_session_id'] = 'session_123'
        sess['booking'] = {'seat_1': {'price': 50000}, 'seat_2': {'price': 100000}}

    # 5. GỬI REQUEST
    response = test_client.post('/checkout', data={'showtime_id': st_mock.id})

    assert response.status_code == 200

    args, kwargs = mock_render.call_args
    assert args[0] == 'checkout.html'

    assert kwargs['stats']['total_amount'] == 150000
    assert kwargs['time_remaining'] > 0
    assert kwargs['showtime'] == st_mock
    assert kwargs['movie'] == st_mock.movie
