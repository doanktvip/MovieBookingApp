from unittest.mock import patch

from movieapp import dao, db
from movieapp.models import SeatStatus
# Import các fixture cần thiết từ test_base
from movieapp.test.conftest import (
    test_app, sample_showtimes_complex
)


def test_clear_db_booking_by_session_none(test_app):
    with test_app.app_context():
        dao.clear_db_booking_by_session(None)


# Test dọn dẹp thành công - Đã sửa lỗi Session
def test_clear_db_booking_by_session_success(test_app, sample_showtimes_complex):
    with test_app.app_context():
        session_id = "my-temp-session-123"
        # Dùng merge để gắn st_seat vào Session hiện tại
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = session_id
        db.session.commit()

        dao.clear_db_booking_by_session(session_id)

        st_seat = db.session.merge(st_seat)
        db.session.refresh(st_seat)

        assert st_seat.status == SeatStatus.AVAILABLE
        assert st_seat.hold_session_id is None


# Test không dọn dẹp nhầm - Đã sửa lỗi Session
def test_clear_db_booking_by_session_no_match(test_app, sample_showtimes_complex):
    with test_app.app_context():
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = "user-A-session"
        db.session.commit()

        dao.clear_db_booking_by_session("user-B-session")

        st_seat = db.session.merge(st_seat)
        db.session.refresh(st_seat)
        assert st_seat.status == SeatStatus.RESERVED


# Test Exception - Dùng Mock để an toàn (không làm hỏng DB engine)
def test_clear_db_booking_by_session_exception_v2(test_app):
    with test_app.app_context():
        with patch.object(db.session, 'commit', side_effect=Exception("Lỗi commit giả lập")):
            dao.clear_db_booking_by_session("any-session-id")
