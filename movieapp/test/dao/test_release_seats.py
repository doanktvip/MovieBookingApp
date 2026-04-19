from unittest.mock import patch
import pytest
from datetime import datetime, timedelta
from movieapp import dao, db
from movieapp.models import SeatStatus, BookingStatus, Ticket, Booking, ShowtimeSeat



# CÁC TRƯỜNG HỢP VỀ THỜI GIAN VÀ TRẠNG THÁI BOOKING
@pytest.mark.parametrize("hold_offset, init_booking_status, expected_seat_status, expected_booking_status", [
    (-10, BookingStatus.PENDING, SeatStatus.AVAILABLE, BookingStatus.FAILED),
    (10, BookingStatus.PENDING, SeatStatus.RESERVED, BookingStatus.PENDING),
    (-10, BookingStatus.PAID, SeatStatus.AVAILABLE, BookingStatus.PAID),
], ids=["expired_pending", "not_expired_pending", "expired_paid"])
def test_release_expired_seats_logic(test_app, sample_users, sample_showtimes_complex,
                                     hold_offset, init_booking_status, expected_seat_status, expected_booking_status):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        showtime = sample_showtimes_complex["showtime"]

        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][0])

        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_until = datetime.now() + timedelta(minutes=hold_offset)
        st_seat.hold_session_id = "test_session_123"

        booking = Booking(user_id=user.id, showtime_id=showtime.id,
                          total_price=st_seat.price, status=init_booking_status)
        db.session.add(booking)
        db.session.flush()

        ticket = Ticket(booking_id=booking.id, showtime_seat_id=st_seat.id, final_price=st_seat.price)
        db.session.add(ticket)

        db.session.commit()

        dao.release_expired_seats()

        st_seat_check = db.session.get(ShowtimeSeat, st_seat.id)
        booking_check = db.session.get(Booking, booking.id)

        assert st_seat_check.status == expected_seat_status
        assert booking_check.status == expected_booking_status

        if expected_seat_status == SeatStatus.AVAILABLE:
            assert st_seat_check.hold_until is None
            assert st_seat_check.hold_session_id is None


# LỌC THEO SUẤT CHIẾU CỤ THỂ (SHOWTIME_ID)
def test_release_expired_seats_specific_showtime(test_app, sample_showtimes_complex):
    with test_app.app_context():
        seat_target = db.session.merge(sample_showtimes_complex["showtime_seats"][0])
        seat_other = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        now = datetime.now()
        for seat in [seat_target, seat_other]:
            seat.status = SeatStatus.RESERVED
            seat.hold_until = now - timedelta(minutes=5)

        seat_other.showtime_id = 9999
        db.session.commit()

        dao.release_expired_seats(showtime_id=seat_target.showtime_id)

        seat_target_check = db.session.get(ShowtimeSeat, seat_target.id)
        seat_other_check = db.session.get(ShowtimeSeat, seat_other.id)

        assert seat_target_check.status == SeatStatus.AVAILABLE
        assert seat_other_check.status == SeatStatus.RESERVED


def test_release_expired_seats_exception_handling(test_app):
    with test_app.app_context():
        # Sử dụng patch để ép db.session.query ném ra một Exception
        with patch.object(db.session, 'query', side_effect=Exception("Lỗi DB giả lập")):
            with pytest.raises(Exception) as excinfo:
                dao.release_expired_seats()

            assert "Lỗi DB giả lập" in str(excinfo.value)
