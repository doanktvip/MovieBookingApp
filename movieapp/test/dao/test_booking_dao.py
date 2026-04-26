import pytest
from datetime import datetime, timedelta
from movieapp import dao, db
from movieapp.models import Booking, Ticket, BookingStatus, SeatStatus, ShowtimeSeat


# CÁC RÀNG BUỘC KHI ĐẶT GHẾ
@pytest.mark.parametrize("scenario, expected_success, expected_msg_snippet", [
    ("success", True, "Giữ ghế thành công"),
    ("invalid_showtime", False, "Suất chiếu không tồn tại"),
    ("movie_started", False, "không thể đặt vé"),
    ("exceed_8_seats", False, "tối đa 8 ghế"),
    ("invalid_seat_id", False, "không hợp lệ"),
    ("seat_booked", False, "người khác nhanh tay chọn mất"),
    ("seat_reserved_by_other", False, "người khác nhanh tay chọn mất"),
])
def test_process_seat_reservations(test_app, sample_users, sample_showtimes_complex,
                                   scenario, expected_success, expected_msg_snippet):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        # Dùng merge() để nạp lại đối tượng vào session hiện tại
        showtime = db.session.merge(sample_showtimes_complex["showtime"])
        seats = [db.session.merge(s) for s in sample_showtimes_complex["showtime_seats"]]

        # --- CÁC BẢN VÁ LỖI DỮ LIỆU TỪ TEST_BASE ---
        showtime.start_time = datetime.now() + timedelta(hours=1)
        db.session.commit()

        target_seats = seats[:2]
        selected_seats_input = [{"id": s.id, "name": f"Seat_{s.id}"} for s in target_seats]
        target_showtime_id = showtime.id

        # Đảm bảo 2 ghế mục tiêu mang đi test phải hoàn toàn trống
        for s in target_seats:
            s.status = SeatStatus.AVAILABLE
            s.hold_session_id = None
            s.hold_until = None
        db.session.commit()

        if scenario == "invalid_showtime":
            target_showtime_id = 9999

        elif scenario == "movie_started":
            showtime.start_time = datetime.now() - timedelta(minutes=10)
            db.session.commit()

        elif scenario == "exceed_8_seats":
            booking = Booking(user_id=user.id, showtime_id=showtime.id, total_price=100000, status=BookingStatus.PAID)
            db.session.add(booking)
            db.session.flush()
            for i in range(7):
                t = Ticket(booking_id=booking.id, showtime_seat_id=seats[0].id, final_price=50000)
                db.session.add(t)
            db.session.commit()

        elif scenario == "invalid_seat_id":
            selected_seats_input.append({"id": 9999, "name": "Ghost_Seat"})

        elif scenario == "seat_booked":
            target_seats[0].status = SeatStatus.BOOKED
            db.session.commit()

        elif scenario == "seat_reserved_by_other":
            target_seats[0].status = SeatStatus.RESERVED
            target_seats[0].hold_session_id = 9999
            target_seats[0].hold_until = datetime.now() + timedelta(minutes=10)
            db.session.commit()

        success, msg, booking_dict, expire_time = dao.process_seat_reservations_secure(
            user_id=user.id,
            showtime_id=target_showtime_id,
            selected_seats=selected_seats_input
        )

        assert success == expected_success
        assert expected_msg_snippet in msg

        if success:
            assert len(booking_dict) == len(selected_seats_input)
            assert expire_time is not None

            for s in target_seats:
                st_seat_check = db.session.get(ShowtimeSeat, s.id)
                assert st_seat_check.status == SeatStatus.RESERVED
                assert st_seat_check.hold_session_id == user.id


def test_release_unselected_seats(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]

        showtime = db.session.merge(sample_showtimes_complex["showtime"])
        seats = [db.session.merge(s) for s in sample_showtimes_complex["showtime_seats"]]

        showtime.start_time = datetime.now() + timedelta(hours=1)
        db.session.commit()

        seat_a = seats[0]
        seat_a.status = SeatStatus.RESERVED
        seat_a.hold_session_id = user.id
        seat_a.hold_until = datetime.now() + timedelta(minutes=10)

        seat_b = seats[1]
        seat_b.status = SeatStatus.AVAILABLE
        db.session.commit()

        selected_seats_input = [{"id": seat_b.id, "name": "Seat_B"}]

        success, _, _, _ = dao.process_seat_reservations_secure(
            user.id, showtime.id, selected_seats_input
        )

        assert success is True

        seat_a_check = db.session.get(ShowtimeSeat, seat_a.id)
        seat_b_check = db.session.get(ShowtimeSeat, seat_b.id)

        assert seat_a_check.status == SeatStatus.AVAILABLE
        assert seat_a_check.hold_session_id is None

        assert seat_b_check.status == SeatStatus.RESERVED
        assert seat_b_check.hold_session_id == user.id


# HÀM count_bookings_by_user
def test_count_bookings_by_user_has_data(test_app, sample_full_chain):
    with test_app.app_context():
        user1 = sample_full_chain["users"]["user1"]
        count = dao.count_bookings_by_user(user1.id)
        assert count == 1


def test_count_bookings_by_user_zero(test_app, sample_users):
    with test_app.app_context():
        user2 = sample_users["users"]["user2"]
        count = dao.count_bookings_by_user(user2.id)
        assert count == 0


def test_count_bookings_by_user_invalid_id(test_app):
    with test_app.app_context():
        count = dao.count_bookings_by_user(9999)
        assert count == 0
