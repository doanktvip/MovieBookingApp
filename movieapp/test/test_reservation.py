import pytest
from datetime import datetime, timedelta
from movieapp import dao, db
from movieapp.models import SeatStatus, ShowtimeSeat
# Import các fixture từ test_base
from movieapp.test.test_base import (
    test_app, test_session, sample_showtimes_complex,
    sample_movies_data, sample_cinemas, sample_basic_setup)


# Test trường hợp session_id là None
def test_get_reservation_expiry_time_no_session(test_app):
    with test_app.app_context():
        result = dao.get_reservation_expiry_time(None, 1)
        assert result is None


# Test trường hợp tìm thấy ghế đang giữ và còn hạn
def test_get_reservation_expiry_time_valid(test_app, sample_showtimes_complex):
    with test_app.app_context():
        session_id = "active-session-123"
        showtime = sample_showtimes_complex["showtime"]
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        # Thiết lập ghế đang được giữ, hết hạn sau 10 phút
        future_time = datetime.utcnow() + timedelta(minutes=10)
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = session_id
        st_seat.hold_until = future_time
        db.session.commit()

        result = dao.get_reservation_expiry_time(session_id, showtime.id)

        assert result is not None
        assert result.strftime('%Y-%m-%d %H:%M') == future_time.strftime('%Y-%m-%d %H:%M')


# Test trường hợp ghế đã hết hạn
def test_get_reservation_expiry_time_expired(test_app, sample_showtimes_complex):
    with test_app.app_context():
        session_id = "expired-session-456"
        showtime = sample_showtimes_complex["showtime"]
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        # Thiết lập ghế đã hết hạn từ 5 phút trước
        past_time = datetime.utcnow() - timedelta(minutes=5)
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = session_id
        st_seat.hold_until = past_time
        db.session.commit()

        result = dao.get_reservation_expiry_time(session_id, showtime.id)

        assert result is None


# Test trường hợp không tìm thấy ghế nào khớp với session_id
def test_get_reservation_expiry_time_no_match(test_app, sample_showtimes_complex):
    with test_app.app_context():
        showtime = sample_showtimes_complex["showtime"]

        result = dao.get_reservation_expiry_time("non-existent-session", showtime.id)

        assert result is None
