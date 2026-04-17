import pytest
from unittest.mock import patch, MagicMock


# --- TEST 1: TẢI TRANG DANH SÁCH (METHOD GET) ---
@patch('movieapp.index.render_template')
@patch('movieapp.index.dao.get_page_range')
@patch('movieapp.index.dao.load_bookings_for_checkin')
def test_check_in_get_success(mock_load_bookings, mock_page_range, mock_render, test_client, sample_users):
    # 1. Giả lập dữ liệu trả về từ các hàm DAO
    mock_load_bookings.return_value = (['booking1', 'booking2'], 5)  # (danh sách, tổng số trang)
    mock_page_range.return_value = [1, 2, 3]
    mock_render.return_value = "Mocked HTML"

    staff_id = str(sample_users["users"]["staff"].id)
    with test_client.session_transaction() as sess:
        sess['_user_id'] = staff_id

    # 3. Gửi request dạng GET có kèm tham số tìm kiếm
    response = test_client.get('/check_in?keyword=Nguyen&page=1')

    assert response.status_code == 200

    # 4. Kiểm tra xem dữ liệu có được đẩy đúng vào HTML không
    args, kwargs = mock_render.call_args
    assert args[0] == 'staff_check_in.html'
    assert kwargs['keyword'] == 'Nguyen'
    assert kwargs['bookings'] == ['booking1', 'booking2']
    assert kwargs['pages'] == 5


# --- TEST 2: CHECK-IN VÉ THÀNH CÔNG (METHOD POST) ---
@patch('movieapp.index.db.session.commit')
@patch('movieapp.index.Booking')
def test_check_in_post_success(mock_booking_model, mock_commit, test_client, sample_users):

    # 1. TẠO RA MỘT CÁI VÉ GIẢ (MagicMock)
    mock_ticket = MagicMock()
    mock_ticket.is_checked_in = False  # Ban đầu chưa check-in

    # 2. TẠO RA MỘT ĐƠN HÀNG GIẢ (Chứa cái vé giả ở trên)
    mock_booking = MagicMock()
    mock_booking.tickets = [mock_ticket]

    # 3. ÉP SQLALCHEMY TRẢ VỀ ĐƠN HÀNG GIẢ KHI TÌM KIẾM
    mock_booking_model.query.get.return_value = mock_booking

    staff_id = str(sample_users["users"]["staff"].id)
    with test_client.session_transaction() as sess:
        sess['_user_id'] = staff_id

    # 4. Gửi request POST (giả lập việc nhân viên bấm nút)
    response = test_client.post('/check_in', data={'submit_checkin': 999})

    # Kiểm tra chuyển hướng về lại trang check_in
    assert response.status_code == 302
    assert response.location == '/check_in'

    # Kiểm tra trạng thái vé đã hoạt động (Từ False thành True)
    assert mock_ticket.is_checked_in is True

    # Kiểm tra đã gọi lệnh lưu Database (db.session.commit) đúng 1 lần
    mock_commit.assert_called_once()


# --- TEST 3: LỖI DATABASE KHI CHECK-IN ---
@patch('movieapp.index.db.session.rollback')
@patch('movieapp.index.db.session.commit')
@patch('movieapp.index.Booking')
def test_check_in_post_db_error(mock_booking_model, mock_commit, mock_rollback, test_client, sample_users):
    mock_ticket = MagicMock()
    mock_booking = MagicMock()
    mock_booking.tickets = [mock_ticket]
    mock_booking_model.query.get.return_value = mock_booking

    #Ép hàm commit() văng lỗi (Crash)
    mock_commit.side_effect = Exception("Database mất kết nối!")

    staff_id = str(sample_users["users"]["staff"].id)
    with test_client.session_transaction() as sess:
        sess['_user_id'] = staff_id

    response = test_client.post('/check_in', data={'submit_checkin': 999})

    # Vẫn chuyển hướng về trang cũ
    assert response.status_code == 302
    assert response.location == '/check_in'

    # KHẲNG ĐỊNH QUAN TRỌNG NHẤT: Hàm db.session.rollback() phải được gọi để chống rác DB!
    mock_rollback.assert_called_once()