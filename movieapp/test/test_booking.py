from datetime import datetime, timedelta
import pytest
from movieapp.dao import create_pending_booking, update_status_booking
from movieapp.models import Booking, BookingStatus, ShowtimeSeat, SeatStatus
from movieapp.test.test_base import test_session, test_app, sample_full_chain, sample_users, sample_showtimes_complex, \
    sample_movies_data, sample_cinemas, sample_basic_setup


# ==========================================
# KIỂM THỬ HÀM TẠO ĐƠN HÀNG (CREATE)
# ==========================================

def test_create_booking_empty(sample_showtimes_complex, sample_users):
    """Kiểm tra trường hợp giỏ hàng trống - Dùng sample_showtimes_complex để tránh data rác"""
    data_st = sample_showtimes_complex
    user = sample_users["users"]["user1"]
    booking_session_empty = {}

    with pytest.raises(Exception, match='Đơn hàng trống!'):
        create_pending_booking(
            user_id=user.id,
            showtime_id=data_st["showtime"].id,
            total_amount=0,
            booking_session=booking_session_empty
        )


def test_create_booking_new(sample_showtimes_complex, sample_users):
    """Kiểm tra tạo đơn hàng mới với 2 ghế - Dùng fixture chưa có booking"""
    data_st = sample_showtimes_complex
    user = sample_users["users"]["user1"]

    # Lấy 2 ghế trống từ fixture
    seat1 = data_st["showtime_seats"][1]
    seat2 = data_st["showtime_seats"][2]

    booking_session = {
        str(seat1.seat_id): {"price": 50000},
        str(seat2.seat_id): {"price": 50000}
    }

    booking_id = create_pending_booking(
        user.id,
        data_st["showtime"].id,
        100000,
        booking_session
    )

    booking = Booking.query.get(booking_id)
    assert booking is not None
    assert booking.status == BookingStatus.PENDING
    assert len(booking.tickets) == 2


def test_create_booking_recontinue_pay(sample_showtimes_complex, sample_users):
    """Kiểm tra khách hàng quay lại thanh toán đơn hàng đang chờ"""
    data_st = sample_showtimes_complex
    user = sample_users["users"]["user1"]
    st_id = data_st["showtime"].id
    seat_id = str(data_st["showtime_seats"][1].seat_id)

    booking_session = {seat_id: {"price": 50000}}

    # Tạo lần 1
    id1 = create_pending_booking(user.id, st_id, 50000, booking_session)
    # Tạo lần 2 (cùng session) -> Trả về cùng ID
    id2 = create_pending_booking(user.id, st_id, 45000, booking_session)

    assert id1 == id2
    booking = Booking.query.get(id1)
    assert booking.total_price == 45000


# ==========================================
# KIỂM THỬ HÀM CẬP NHẬT TRẠNG THÁI (UPDATE)
# ==========================================

def test_update_booking_status_not_found(test_app):
    with test_app.app_context():
        with pytest.raises(Exception, match="Không tìm thấy đơn hàng!"):
            update_status_booking(booking_id=9999, status=BookingStatus.PAID, current_sid="abc")


def test_update_booking_status_success(sample_full_chain, test_session):
    """Dùng sample_full_chain vì hàm này cần 1 booking có sẵn để thanh toán"""
    data = sample_full_chain
    booking = data["booking"]
    st_seat = data["showtime_seats"][1]

    session_id = "test_session_123"
    st_seat.status = SeatStatus.RESERVED
    st_seat.hold_session_id = session_id
    st_seat.hold_until = datetime.utcnow() + timedelta(minutes=10)
    test_session.commit()

    update_status_booking(booking.id, BookingStatus.PAID, session_id)

    assert booking.status == BookingStatus.PAID
    assert st_seat.status == SeatStatus.BOOKED


def test_update_status_booking_wrong_session(sample_full_chain, test_session):
    """Bảo mật: Session ID không khớp"""
    data = sample_full_chain
    st_seat = data["showtime_seats"][1]

    st_seat.hold_session_id = "session_real"
    test_session.commit()

    with pytest.raises(Exception, match="đã hết thời gian giữ và bị người khác lấy"):
        update_status_booking(data["booking"].id, BookingStatus.PAID, "session_hacker")


def test_update_status_booking_expire_paying(sample_full_chain, test_session):
    """Hết hạn thời gian giữ ghế"""
    data = sample_full_chain
    st_seat = data["showtime_seats"][1]
    session_id = "session_123"

    st_seat.hold_session_id = session_id
    st_seat.hold_until = datetime.utcnow() - timedelta(minutes=1)
    test_session.commit()

    with pytest.raises(Exception, match="Giao dịch trễ!"):
        update_status_booking(data["booking"].id, BookingStatus.PAID, session_id)
