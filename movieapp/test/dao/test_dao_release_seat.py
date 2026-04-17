from unittest.mock import patch
import pytest
from movieapp import dao
from movieapp.models import SeatStatus


# TEST HÀM: release_single_seat_db
# Test giải phóng ghế thành công khi đúng ID và Session ID
def test_release_single_seat_db_success(test_session, sample_showtimes_complex):
    # Lấy một ghế mẫu từ dữ liệu conftest
    target_seat = sample_showtimes_complex["showtime_seats"][1]  # Ghế đang AVAILABLE
    mock_session_id = "test-session-123"

    # Giả lập trạng thái ghế đang được giữ bởi session này
    target_seat.status = SeatStatus.RESERVED
    target_seat.hold_session_id = mock_session_id
    test_session.commit()

    # Gọi hàm cần test
    dao.release_single_seat_db(target_seat.id, mock_session_id)

    # Kiểm tra dữ liệu sau khi hàm chạy
    test_session.refresh(target_seat)

    assert target_seat.status == SeatStatus.AVAILABLE
    assert target_seat.hold_session_id is None
    assert target_seat.hold_until is None


# Test không giải phóng ghế nếu Session ID không khớp (bảo mật)
def test_release_single_seat_db_wrong_session(test_session, sample_showtimes_complex):
    target_seat = sample_showtimes_complex["showtime_seats"][1]
    owner_session_id = "owner-session"
    intruder_session_id = "intruder-session"

    # Giả lập ghế đang được giữ bởi 'owner'
    target_seat.status = SeatStatus.RESERVED
    target_seat.hold_session_id = owner_session_id
    test_session.commit()

    # Hành động: Một session khác cố tình gọi lệnh giải phóng ghế này
    dao.release_single_seat_db(target_seat.id, intruder_session_id)

    # Kiểm tra: Ghế phải giữ nguyên trạng thái RESERVED của chủ cũ
    test_session.refresh(target_seat)
    assert target_seat.status == SeatStatus.RESERVED
    assert target_seat.hold_session_id == owner_session_id

# Test trường hợp Exception
@patch('movieapp.dao.db.session.commit')
def test_release_single_seat_db_exception(mock_commit, test_session, sample_showtimes_complex):
    # Cấu hình side_effect theo danh sách:
    # Lần gọi 1: Trả về None (Thành công)
    # Lần gọi 2: Ném lỗi (Thất bại)
    mock_commit.side_effect = [None, Exception("Lỗi Database giả lập")]

    # 1. Chuẩn bị dữ liệu - Lệnh này gọi commit lần 1 -> Thành công
    target_seat = sample_showtimes_complex["showtime_seats"][1]
    mock_session_id = "session-error-test"

    target_seat.status = SeatStatus.RESERVED
    target_seat.hold_session_id = mock_session_id
    test_session.commit()

    # 2. Gọi hàm dao - Lệnh commit bên trong hàm dao là lần gọi 2 -> Ném lỗi
    dao.release_single_seat_db(target_seat.id, mock_session_id)

    # Kiểm tra xem commit đã được gọi tổng cộng 2 lần chưa
    assert mock_commit.call_count == 2


# Test thêm trường hợp Session ID là None hoặc Rỗng
def test_release_single_seat_db_invalid_params(test_session, sample_showtimes_complex):
    target_seat = sample_showtimes_complex["showtime_seats"][1]

    # Trường hợp ID đúng nhưng Session ID bị None
    dao.release_single_seat_db(target_seat.id, None)

    # Trường hợp ID bị None
    dao.release_single_seat_db(None, "some-session")

    test_session.refresh(target_seat)
    # Ghế không được thay đổi trạng thái
    assert target_seat.status == SeatStatus.AVAILABLE
