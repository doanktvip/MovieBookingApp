from datetime import datetime, timedelta
import pytest
from movieapp.dao import create_pending_booking, update_status_booking
from movieapp.models import Booking, BookingStatus, ShowtimeSeat, SeatStatus
from movieapp.test.test_base import test_session, test_app, sample_full_chain, sample_users, sample_showtimes_complex, \
    sample_movies_data, sample_cinemas, sample_basic_setup
from unittest.mock import patch


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

#Khách đổi thêm bớt ghế để thanh toán lại
def test_create_booking_different_seat(sample_showtimes_complex,sample_users):
    data_st=sample_showtimes_complex
    user = sample_users["users"]["user1"]
    st_id = data_st["showtime"].id
    seat_id_1 = str(data_st["showtime_seats"][1].seat_id)
    seat_id_2=str(data_st["showtime_seats"][2].seat_id)
    seat_id_3 = str(data_st["showtime_seats"][2].seat_id)

    # Tạo lần 1
    booking_session_1 = {seat_id_1: {"price": 50000}}
    id1 = create_pending_booking(user.id, st_id, 50000, booking_session_1)

    #Thêm bớt ghế lần 2
    booking_session_2={seat_id_1: {"price": 50000},seat_id_2: {"price": 50000}}
    id2 = create_pending_booking(user.id, st_id, 100000, booking_session_2)

    # Lúc này CSDL chỉ còn đơn mới đơn cũ bị xóa
    assert Booking.query.count() == 1

    # Kiểm tra đơn mới có đủ 3 ghế??
    new_booking = Booking.query.get(id2)
    assert new_booking is not None
    assert new_booking.status == BookingStatus.PENDING
    assert len(new_booking.tickets) == 2

def test_create_booking_db_commit_error(sample_showtimes_complex, sample_users):
    data_st = sample_showtimes_complex
    user = sample_users["users"]["user1"]
    st_id = data_st["showtime"].id
    seat_id = str(data_st["showtime_seats"][1].seat_id)
    booking_session = {seat_id: {"price": 50000}}
    total_amount = 50000
    with patch("movieapp.db.session.commit") as mock_commit:
        # Giả lập lỗi kết nối database
        mock_commit.side_effect = Exception("Database Connection Error")

        # Kiểm tra xem hàm có raise đúng lỗi Exception đã giả lập hay không
        with pytest.raises(Exception, match="Database Connection Error"):
            create_pending_booking(
                user_id=user.id,
                showtime_id=st_id,
                total_amount=total_amount,
                booking_session=booking_session
            )

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

def test_update_status_booking_canceled_paying(sample_full_chain, test_session):
    data = sample_full_chain
    session_id = "session_123"
    st_seat = data["showtime_seats"][1]
    booking = data["booking"]
    st_seat.hold_session_id = session_id
    st_seat.status = SeatStatus.RESERVED
    test_session.commit()

    result=update_status_booking(booking.id, BookingStatus.PENDING, session_id)

    assert result is not None
    assert booking.status == BookingStatus.PENDING

    #Kiểm tra ghế tiếp tục giữ
    st_seat_check = ShowtimeSeat.query.get(st_seat.id)
    assert st_seat.status == SeatStatus.RESERVED
    assert st_seat.hold_session_id == session_id

def test_update_status_booking_cancelled_paying(sample_full_chain):
    data = sample_full_chain
    booking_id = data["booking"].id

    # Mock lệnh commit để ra lỗi
    with patch("movieapp.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("Database is down")

        with pytest.raises(Exception, match="Database is down"):
            update_status_booking(booking_id, BookingStatus.PAID)