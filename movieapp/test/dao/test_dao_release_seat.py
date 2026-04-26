from unittest.mock import patch
from movieapp import dao
from movieapp.models import SeatStatus


# TEST HÀM: release_single_seat_db
def test_release_single_seat_db_success(test_session, sample_showtimes_complex):
    target_seat = sample_showtimes_complex["showtime_seats"][1]  # Ghế đang AVAILABLE

    mock_session_id = 123

    target_seat.status = SeatStatus.RESERVED
    target_seat.hold_session_id = mock_session_id
    test_session.commit()

    dao.release_single_seat_db(target_seat.id, mock_session_id)

    test_session.refresh(target_seat)

    assert target_seat.status == SeatStatus.AVAILABLE
    assert target_seat.hold_session_id is None
    assert target_seat.hold_until is None


# Test không giải phóng ghế nếu Session ID không khớp (bảo mật)
def test_release_single_seat_db_wrong_session(test_session, sample_showtimes_complex):
    target_seat = sample_showtimes_complex["showtime_seats"][1]

    owner_session_id = 888
    intruder_session_id = 999

    target_seat.status = SeatStatus.RESERVED
    target_seat.hold_session_id = owner_session_id
    test_session.commit()

    dao.release_single_seat_db(target_seat.id, intruder_session_id)

    test_session.refresh(target_seat)
    assert target_seat.status == SeatStatus.RESERVED
    assert target_seat.hold_session_id == owner_session_id


# Test trường hợp Exception
@patch('movieapp.dao.db.session.commit')
def test_release_single_seat_db_exception(mock_commit, test_session, sample_showtimes_complex):
    mock_commit.side_effect = [None, Exception("Lỗi Database giả lập")]

    target_seat = sample_showtimes_complex["showtime_seats"][1]

    mock_session_id = 123

    target_seat.status = SeatStatus.RESERVED
    target_seat.hold_session_id = mock_session_id
    test_session.commit()

    dao.release_single_seat_db(target_seat.id, mock_session_id)

    assert mock_commit.call_count == 2


# Test thêm trường hợp Session ID là None hoặc Rỗng
def test_release_single_seat_db_invalid_params(test_session, sample_showtimes_complex):
    target_seat = sample_showtimes_complex["showtime_seats"][1]
    dao.release_single_seat_db(target_seat.id, None)
    dao.release_single_seat_db(None, 999)

    test_session.refresh(target_seat)
    assert target_seat.status == SeatStatus.AVAILABLE
