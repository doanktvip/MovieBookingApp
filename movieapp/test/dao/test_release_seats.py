from unittest.mock import patch
import pytest
from datetime import datetime, timedelta
from movieapp import dao, db
from movieapp.models import SeatStatus, BookingStatus, Ticket, Booking, ShowtimeSeat


# 1. TEST: HÀM release_expired_seats
@pytest.mark.parametrize("hold_offset, init_booking_status, expected_seat_status, expected_booking_status", [
    # Trường hợp 1: Ghế hết hạn, Booking PENDING -> Booking bị XÓA (None), Ghế AVAILABLE
    (-10, BookingStatus.PENDING, SeatStatus.AVAILABLE, None),
    # Trường hợp 2: Ghế chưa hết hạn, Booking PENDING -> Giữ nguyên
    (10, BookingStatus.PENDING, SeatStatus.RESERVED, BookingStatus.PENDING),
    # Trường hợp 3: Ghế hết hạn, Booking PAID -> Vé không bị xóa, Booking giữ nguyên PAID, Ghế được set AVAILABLE
    (-10, BookingStatus.PAID, SeatStatus.AVAILABLE, BookingStatus.PAID),
], ids=["expired_pending_deleted", "not_expired_pending", "expired_paid"])
def test_release_expired_seats_logic(test_app, sample_users, sample_showtimes_complex,
                                     hold_offset, init_booking_status, expected_seat_status, expected_booking_status):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        showtime = sample_showtimes_complex["showtime"]

        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][0])
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_until = datetime.now() + timedelta(minutes=hold_offset)
        st_seat.hold_session_id = user.id

        # Tạo Booking và Ticket
        booking = Booking(user_id=user.id, showtime_id=showtime.id,
                          total_price=st_seat.price, status=init_booking_status)
        db.session.add(booking)
        db.session.flush()

        ticket = Ticket(booking_id=booking.id, showtime_seat_id=st_seat.id, final_price=st_seat.price)
        db.session.add(ticket)
        db.session.commit()

        # Thực thi hàm
        dao.release_expired_seats()

        # Kiểm tra kết quả
        st_seat_check = db.session.get(ShowtimeSeat, st_seat.id)
        booking_check = db.session.get(Booking, booking.id)

        assert st_seat_check.status == expected_seat_status
        if expected_seat_status == SeatStatus.AVAILABLE:
            assert st_seat_check.hold_until is None
            assert st_seat_check.hold_session_id is None

        # Kiểm tra trạng thái Booking mới (cho phép None nếu đã bị xóa)
        if expected_booking_status is None:
            assert booking_check is None  # Đảm bảo Booking PENDING đã bị xóa
        else:
            assert booking_check is not None
            assert booking_check.status == expected_booking_status


def test_release_expired_seats_specific_showtime(test_app, sample_showtimes_complex):
    with test_app.app_context():
        seat_target = db.session.merge(sample_showtimes_complex["showtime_seats"][0])
        seat_other = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        now = datetime.now()
        for seat in [seat_target, seat_other]:
            seat.status = SeatStatus.RESERVED
            seat.hold_until = now - timedelta(minutes=5)
            seat.hold_session_id = 123

        seat_other.showtime_id = 9999
        db.session.commit()

        dao.release_expired_seats(showtime_id=seat_target.showtime_id)

        seat_target_check = db.session.get(ShowtimeSeat, seat_target.id)
        seat_other_check = db.session.get(ShowtimeSeat, seat_other.id)

        assert seat_target_check.status == SeatStatus.AVAILABLE
        assert seat_other_check.status == SeatStatus.RESERVED


@patch('movieapp.dao.db.session.rollback')
def test_release_expired_seats_exception_handling(mock_rollback, test_app):
    with test_app.app_context():
        # Hàm mới đã dùng try-except nên ta kiểm tra xem rollback có được gọi khi có lỗi không
        with patch.object(db.session, 'query', side_effect=Exception("Lỗi DB giả lập")):
            dao.release_expired_seats()
            mock_rollback.assert_called_once()


# HÀM release_single_seat_db
@pytest.mark.parametrize("has_multiple_tickets, init_booking_status", [
    (False, BookingStatus.PENDING),  # Xóa vé và xóa luôn Booking (do rỗng)
    (True, BookingStatus.PENDING),  # Xóa vé nhưng giữ lại Booking (vì còn vé khác)
    (False, BookingStatus.PAID),  # Bỏ qua if ticket, chỉ update ghế (vì vé đã thanh toán)
], ids=["delete_ticket_and_booking", "delete_ticket_keep_booking", "ignore_paid_ticket"])
def test_release_single_seat_db_coverage(test_app, sample_users, sample_showtimes_complex,
                                         has_multiple_tickets, init_booking_status):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        showtime = sample_showtimes_complex["showtime"]

        session_id = user.id

        # Setup ghế 1
        seat1 = db.session.merge(sample_showtimes_complex["showtime_seats"][0])
        seat1.status = SeatStatus.RESERVED
        seat1.hold_session_id = session_id
        seat1.hold_until = datetime.now() + timedelta(minutes=10)

        # Tạo Booking
        booking = Booking(user_id=user.id, showtime_id=showtime.id, total_price=seat1.price, status=init_booking_status)
        db.session.add(booking)
        db.session.flush()

        # Thêm vé 1
        ticket1 = Ticket(booking_id=booking.id, showtime_seat_id=seat1.id, final_price=seat1.price)
        db.session.add(ticket1)

        # Thêm vé 2 (nếu test trường hợp đơn có nhiều vé)
        if has_multiple_tickets:
            seat2 = db.session.merge(sample_showtimes_complex["showtime_seats"][1])
            seat2.status = SeatStatus.RESERVED
            seat2.hold_session_id = session_id
            ticket2 = Ticket(booking_id=booking.id, showtime_seat_id=seat2.id, final_price=seat2.price)
            db.session.add(ticket2)

        db.session.commit()

        # Thực thi hàm giải phóng ghế 1
        dao.release_single_seat_db(seat1.id, session_id)

        # Kiểm tra dữ liệu sau khi chạy hàm
        seat1_check = db.session.get(ShowtimeSeat, seat1.id)
        booking_check = db.session.get(Booking, booking.id)
        ticket1_check = db.session.get(Ticket, ticket1.id)

        # Ghế luôn phải được chuyển về trạng thái trống
        assert seat1_check.status == SeatStatus.AVAILABLE
        assert seat1_check.hold_session_id is None

        if init_booking_status == BookingStatus.PENDING:
            assert ticket1_check is None  # Nhánh xóa vé

            if has_multiple_tickets:
                assert booking_check is not None  # Nhánh không xóa booking
                assert len(booking_check.tickets) == 1
            else:
                assert booking_check is None  # Nhánh xóa luôn booking
        else:
            assert ticket1_check is not None  # Nhánh không xóa vé (vì PAID)
            assert booking_check is not None


def test_release_single_seat_db_exception(test_app):
    with test_app.app_context():
        # Phủ nhánh except (bắt lỗi DB)
        with patch.object(db.session, 'query', side_effect=Exception("DB Error")):
            dao.release_single_seat_db(1, 123)
