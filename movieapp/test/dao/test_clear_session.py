from unittest.mock import patch
from movieapp import dao, db
from movieapp.models import SeatStatus, Booking, Ticket, BookingStatus


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


def test_clear_db_booking_by_session_with_pending_ticket(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        session_id = user.id
        
        showtime = db.session.merge(sample_showtimes_complex["showtime"])
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = session_id
        db.session.commit()
        
        booking = Booking(user_id=user.id, showtime_id=showtime.id, total_price=50000, status=BookingStatus.PENDING)
        db.session.add(booking)
        db.session.flush()
        ticket = Ticket(booking_id=booking.id, showtime_seat_id=st_seat.id, final_price=50000)
        db.session.add(ticket)
        db.session.commit()
        
        booking_id = booking.id
        ticket_id = ticket.id

        dao.clear_db_booking_by_session(session_id)

        st_seat = db.session.merge(st_seat)
        db.session.refresh(st_seat)

        assert st_seat.status == SeatStatus.AVAILABLE
        assert st_seat.hold_session_id is None
        
        # Check if ticket and booking are deleted
        deleted_ticket = db.session.get(Ticket, ticket_id)
        assert deleted_ticket is None
        deleted_booking = db.session.get(Booking, booking_id)
        assert deleted_booking is None


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
