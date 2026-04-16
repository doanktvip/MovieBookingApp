from unittest.mock import patch

import pytest
from datetime import datetime, timedelta
from movieapp import dao, db
from movieapp.models import BookingStatus, SeatStatus
# Import các fixture từ test_base
from movieapp.test.test_base import (
    test_app, test_session, sample_full_chain, sample_users, sample_showtimes_complex, sample_movies_data,
    sample_cinemas, sample_basic_setup
)


# Test hủy thành công
def test_cancel_booking_success(test_app, sample_full_chain):
    with test_app.app_context():
        booking = db.session.merge(sample_full_chain["booking"])
        user = sample_full_chain["users"]["user1"]

        # Bước quan trọng: Giả lập suất chiếu còn xa (5 tiếng nữa)
        booking.showtime.start_time = datetime.utcnow() + timedelta(hours=5)
        db.session.commit()

        success, message = dao.cancel_booking(booking.id, user.id)

        assert success is True
        assert message == "Đã hủy vé thành công!"

        # Dùng merge để gắn lại st_seat vào session hiện tại trước khi refresh
        st_seat = db.session.merge(sample_full_chain["showtime_seats"][1])
        db.session.refresh(st_seat)
        assert st_seat.status == SeatStatus.AVAILABLE


# Test lỗi: Hủy quá muộn
def test_cancel_booking_too_late(test_app, sample_full_chain):
    with test_app.app_context():
        booking = db.session.merge(sample_full_chain["booking"])
        user = sample_full_chain["users"]["user1"]

        # Giả lập chỉ còn 1 tiếng nữa là chiếu
        booking.showtime.start_time = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        success, message = dao.cancel_booking(booking.id, user.id)

        assert success is False
        assert "ít nhất 2 tiếng" in message


# Test lỗi: Vé đã check-in
def test_cancel_booking_already_checked_in(test_app, sample_full_chain):
    with test_app.app_context():
        booking = db.session.merge(sample_full_chain["booking"])
        user = sample_full_chain["users"]["user1"]

        # Giả lập vé đã check-in
        for ticket in booking.tickets:
            ticket.is_checked_in = True
        db.session.commit()

        success, message = dao.cancel_booking(booking.id, user.id)

        assert success is False
        assert "đã được check-in" in message


# Test lỗi: Không tìm thấy đơn hàng
def test_cancel_booking_not_found(test_app):
    with test_app.app_context():
        # Dùng ID không tồn tại
        success, message = dao.cancel_booking(9999, 1)

        assert success is False
        assert message == "Đơn hàng không tồn tại!"


# Test lỗi hệ thống
def test_cancel_booking_db_exception(test_app, sample_full_chain):
    with test_app.app_context():
        booking = db.session.merge(sample_full_chain["booking"])
        user = sample_full_chain["users"]["user1"]

        # Phải đảm bảo suất chiếu thỏa mãn điều kiện > 2h trước
        booking.showtime.start_time = datetime.utcnow() + timedelta(hours=5)
        db.session.commit()

        # Giả lập lỗi khi commit
        with patch.object(db.session, 'commit', side_effect=Exception("Lỗi DB giả lập")):
            success, message = dao.cancel_booking(booking.id, user.id)

            assert success is False
            # Bây giờ tin nhắn sẽ đúng là "Lỗi hệ thống"
            assert "Lỗi hệ thống" in message
