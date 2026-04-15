from datetime import datetime, timedelta

import pytest
from movieapp.dao import create_pending_booking,update_status_booking
from movieapp.models import Booking, BookingStatus, Seat, ShowtimeSeat, SeatStatus
from movieapp.test.test_base import test_session, test_app, sample_rooms, sample_users, sample_seats, sample_cinemas, \
    sample_booking_data, sample_update_status,sample_movies


def test_create_booking_empty(sample_rooms,sample_users,sample_seats):
    booking_session_empty = {}
    with pytest.raises(Exception,match='Đơn hàng trống!'):
        create_pending_booking(user_id=1, showtime_id=1, total_amount=0, booking_session=booking_session_empty)

def test_create_booking_new(sample_booking_data):
    data=sample_booking_data
    #Chọn 2 ghế ở booking session
    booking_session={
        data["seat1_id"]: {
            "price":50000
        },
        data["seat2_id"]: {
            "price":50000
        }
    }
    booking_id = create_pending_booking(data["user_id"], data["showtime_id"], 100000, booking_session)
    # Kiểm tra đơn hàng có tồn tại và đúng trạng thái không
    booking = Booking.query.get(booking_id)
    assert booking is not None
    assert booking.status == BookingStatus.PENDING
    assert booking.total_price == 100000

    #Kiểm tra số lượng vé
    assert len(booking.tickets)==2

#Khách giữ ghế thanh toán lại
def test_create_booking_recontinue_pay(sample_booking_data):
    data=sample_booking_data
    booking_session = {
        data["seat1_id"]: {
            "price": 50000
        },
        data["seat2_id"]: {
            "price": 50000
        }
    }
    booking_first = create_pending_booking(data["user_id"], data["showtime_id"], 100000, booking_session)
    booking_second = create_pending_booking(data["user_id"], data["showtime_id"], 80000, booking_session)
    assert booking_first==booking_second
    booking = Booking.query.get(booking_first)
    assert booking.status == BookingStatus.PENDING
    assert booking.total_price == 80000
    assert len(booking.tickets)==2

#Khách đổi thêm bớt ghế để thanh toán lại
def test_create_booking_different_seat(sample_booking_data):
    data=sample_booking_data
    #Lần 1 chọn 1 ghế
    booking_session_1 = {
        data["seat1_id"]: {
            "price": 50000
        }
    }
    booking_id_1=create_pending_booking(data["user_id"],data["showtime_id"],50000,booking_session_1)
    # Lần 2 chọn thêm ghế 2 3
    booking_session_2 = {
        data["seat1_id"]: {
            "price": 50000
        },
        data["seat2_id"]: {
            "price": 50000
        },
        data["seat3_id"]: {
            "price": 50000
        }
    }
    booking_id_2=create_pending_booking(data["user_id"],data["showtime_id"],150000,booking_session_2)
    #Lúc này CSDL chỉ còn đơn mới đơn cũ bị xóa
    assert Booking.query.count() == 1

    #Kiểm tra đơn mới có đủ 3 ghế??
    new_booking=Booking.query.get(booking_id_2)
    assert new_booking is not None
    assert new_booking.status == BookingStatus.PENDING
    assert len(new_booking.tickets) == 3

#TEST HÀM UPDATE STATUS BOOKING
def test_update_booking_status_not_found(sample_update_status):
    with pytest.raises(Exception, match="Không tìm thấy đơn hàng!"):
        update_status_booking(booking_id=9999, status=BookingStatus.PAID, current_sid="abc")

#Thanh toán thành công và đúng hạn
def test_update_booking_status_success(sample_update_status):
    data=sample_update_status
    result=update_status_booking(booking_id=data["booking_id"], status=BookingStatus.PAID, current_sid=data["session_id"])

    assert result is not None
    booking=Booking.query.get(data["booking_id"])
    assert booking.status == BookingStatus.PAID

    st_seat=ShowtimeSeat.query.get(data["st_seat_id"])
    assert st_seat.status == SeatStatus.BOOKED
    assert st_seat.hold_until is None  # Đã xóa đồng hồ đếm ngược
    assert st_seat.hold_session_id is None #Xóa giữ chỗ

#Bảo mật
def test_update_status_booking_wrong_session(sample_update_status):
    data = sample_update_status

    # Cố tình truyền session_id của người khác giả vờ thanh toán
    with pytest.raises(Exception, match="đã hết thời gian giữ và bị người khác lấy"):
        update_status_booking(data["booking_id"], BookingStatus.PAID, "session_999")

#Hết hạn thanh toán
def test_update_status_booking_expire_paying(sample_update_status,test_session):
    data = sample_update_status

    # Ép thời gian của ghế lùi về quá khứ (Tức là đã bị quá hạn)
    st_seat = ShowtimeSeat.query.get(data["st_seat_id"])
    st_seat.hold_until = datetime.utcnow() - timedelta(minutes=5)
    test_session.commit()

    with pytest.raises(Exception, match="Giao dịch trễ! Thời gian giữ ghế đã hết hạn trước khi hệ thống ghi nhận thanh toán."):
        update_status_booking(data["booking_id"], BookingStatus.PAID, data["session_id"])

#Còn thời gian nhưng hủy thanh toán
def test_update_status_booking_canceled_paying(sample_update_status):
    data = sample_update_status
    result = update_status_booking(data["booking_id"], BookingStatus.PENDING, data["session_id"])

    assert result is not None
    booking=Booking.query.get(data["booking_id"])
    assert booking.status == BookingStatus.PENDING

    #Kiểm tra ghế vẫn tiếp tục giữ
    st_seat=ShowtimeSeat.query.get(data["st_seat_id"])
    assert st_seat.status == SeatStatus.RESERVED
    assert st_seat.hold_session_id == data["session_id"]

