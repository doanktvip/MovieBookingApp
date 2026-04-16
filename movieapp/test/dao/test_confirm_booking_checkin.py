from movieapp import db
from movieapp.dao import confirm_booking_checkin
from movieapp.models import Booking, BookingStatus, ShowtimeSeat, SeatStatus
from movieapp.test.conftest import test_session, test_app, sample_full_chain, sample_users, sample_showtimes_complex, \
    sample_movies_data, sample_cinemas, sample_basic_setup
from unittest.mock import patch


def test_confirm_booking_checkin_not_found(test_app):
    with test_app.app_context():
        status, message = confirm_booking_checkin(9999)

        assert status is False
        assert message == "Không tìm thấy đơn hàng"


def test_confirm_booking_checkin_success(sample_full_chain):
    data = sample_full_chain
    booking_id = data['booking'].id
    result = confirm_booking_checkin(booking_id)

    assert result is True

    booking = db.session.get(Booking, booking_id)
    for ticket in booking.tickets:
        assert ticket.is_checked_in is True


def test_confirm_booking_checkin_db_commit_error(sample_full_chain, test_session):
    data = sample_full_chain
    booking_id = data['booking'].id
    with patch("movieapp.db.session.commit") as mock_commit:
        # Giả lập lỗi kết nối database
        mock_commit.side_effect = Exception("Database Connection Error")
        success, message = confirm_booking_checkin(booking_id)

        assert success is False
        assert "Database Connection Error" in message
