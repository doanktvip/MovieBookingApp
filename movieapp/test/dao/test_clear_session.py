from unittest.mock import patch
from movieapp import dao, db
from movieapp.models import SeatStatus


def test_clear_db_booking_by_session_none(test_app):
    with test_app.app_context():
        dao.clear_db_booking_by_session(None)


def test_clear_db_booking_by_session_success(test_app, sample_showtimes_complex):
    with test_app.app_context():
        session_id = 123

        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = session_id
        db.session.commit()

        dao.clear_db_booking_by_session(session_id)

        st_seat = db.session.merge(st_seat)
        db.session.refresh(st_seat)

        assert st_seat.status == SeatStatus.AVAILABLE
        assert st_seat.hold_session_id is None


def test_clear_db_booking_by_session_no_match(test_app, sample_showtimes_complex):
    with test_app.app_context():
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = 888
        db.session.commit()

        dao.clear_db_booking_by_session(999)

        st_seat = db.session.merge(st_seat)
        db.session.refresh(st_seat)
        assert st_seat.status == SeatStatus.RESERVED


def test_clear_db_booking_by_session_exception_v2(test_app):
    with test_app.app_context():
        with patch.object(db.session, 'commit', side_effect=Exception("Lỗi commit giả lập")):
            dao.clear_db_booking_by_session(123)
