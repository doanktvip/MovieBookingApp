import pytest
from datetime import datetime, timedelta
from movieapp import dao, db
from movieapp.models import Booking, Ticket, BookingStatus, SeatStatus, ShowtimeSeat, Showtime
from movieapp.test.test_base import test_app, sample_users, sample_showtimes_complex, test_session, sample_movies_data, \
    sample_cinemas, sample_basic_setup


# =====================================================================
# TEST 1: CÁC RÀNG BUỘC KHI ĐẶT GHẾ (PARAMETRIZED)
# =====================================================================
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
        session_id = "test_user_session_123"

        # Dùng merge() để nạp lại đối tượng vào session hiện tại (Tránh DetachedInstanceError)
        showtime = db.session.merge(sample_showtimes_complex["showtime"])
        seats = [db.session.merge(s) for s in sample_showtimes_complex["showtime_seats"]]

        # --- CÁC BẢN VÁ LỖI DỮ LIỆU TỪ TEST_BASE ---

        # VÁ LỖI 1: Đẩy giờ chiếu lên tương lai (+1 tiếng) để không bị chặn bởi lỗi "phim đã chiếu"
        showtime.start_time = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        # Lấy 2 ghế làm mẫu để mang đi test đặt vé
        target_seats = seats[:2]
        selected_seats_input = [{"id": s.id, "name": f"Seat_{s.id}"} for s in target_seats]
        target_showtime_id = showtime.id

        # VÁ LỖI 2: Đảm bảo 2 ghế mục tiêu mang đi test phải hoàn toàn trống (AVAILABLE)
        # (Vì trong file test_base.py, ghế đầu tiên đang bị set cứng là BOOKED)
        for s in target_seats:
            s.status = SeatStatus.AVAILABLE
            s.hold_session_id = None
            s.hold_until = None
        db.session.commit()

        # ----------------------------------------------------
        # THIẾT LẬP DỮ LIỆU GIẢ LẬP CHO TỪNG KỊCH BẢN TÙY CHỈNH
        # ----------------------------------------------------
        if scenario == "invalid_showtime":
            target_showtime_id = 9999

        elif scenario == "movie_started":
            showtime.start_time = datetime.utcnow() - timedelta(minutes=10)
            db.session.commit()

        elif scenario == "exceed_8_seats":
            # Giả lập User này đã có 7 vé cho suất chiếu hiện tại
            booking = Booking(user_id=user.id, showtime_id=showtime.id, total_price=100000, status=BookingStatus.PAID)
            db.session.add(booking)
            db.session.flush()
            for i in range(7):
                # VÁ LỖI 3: Dùng luôn seats[0].id thay vì seats[i + 2] để tránh lỗi Out of Range
                t = Ticket(booking_id=booking.id, showtime_seat_id=seats[0].id, final_price=50000)
                db.session.add(t)
            db.session.commit()

        elif scenario == "invalid_seat_id":
            # Chèn thêm 1 ghế ma không có trong DB
            selected_seats_input.append({"id": 9999, "name": "Ghost_Seat"})

        elif scenario == "seat_booked":
            # Giả lập ghế đã bị người khác mua đứt
            target_seats[0].status = SeatStatus.BOOKED
            db.session.commit()

        elif scenario == "seat_reserved_by_other":
            # Giả lập ghế đang bị người khác (cùng lúc) giữ chỗ
            target_seats[0].status = SeatStatus.RESERVED
            target_seats[0].hold_session_id = "ANOTHER_USER_SESSION"
            target_seats[0].hold_until = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()

        # ----------------------------------------------------
        # THỰC THI HÀM CẦN TEST
        # ----------------------------------------------------
        success, msg, booking_dict, expire_time = dao.process_seat_reservations_secure(
            user_id=user.id,
            session_id=session_id,
            showtime_id=target_showtime_id,
            selected_seats=selected_seats_input
        )

        # ----------------------------------------------------
        # KIỂM TRA KẾT QUẢ ĐẦU RA
        # ----------------------------------------------------
        assert success == expected_success
        assert expected_msg_snippet in msg

        # NẾU KỊCH BẢN THÀNH CÔNG: Kiểm tra xem Database có lưu đúng không
        if success:
            assert len(booking_dict) == len(selected_seats_input)
            assert expire_time is not None

            for s in target_seats:
                st_seat_check = db.session.get(ShowtimeSeat, s.id)
                assert st_seat_check.status == SeatStatus.RESERVED
                assert st_seat_check.hold_session_id == session_id


# =====================================================================
# TEST 2: KIỂM TRA LOGIC TỰ ĐỘNG NHẢ GHẾ CŨ (KHI BỎ TICK TRÊN GIAO DIỆN)
# =====================================================================
def test_release_unselected_seats(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        session_id = "test_user_session_123"

        showtime = db.session.merge(sample_showtimes_complex["showtime"])
        seats = [db.session.merge(s) for s in sample_showtimes_complex["showtime_seats"]]

        # Đảm bảo giờ chiếu ở tương lai để không bị báo lỗi "phim đã chiếu"
        showtime.start_time = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        # 1. TẠO BỐI CẢNH: Giả sử hôm qua user đã tick chọn giữ Ghế A (id=seats[0].id)
        seat_a = seats[0]
        seat_a.status = SeatStatus.RESERVED
        seat_a.hold_session_id = session_id
        seat_a.hold_until = datetime.utcnow() + timedelta(minutes=10)

        # 2. Hôm nay: User đổi ý, bỏ tick Ghế A và CHỈ CHỌN Ghế B (id=seats[1].id)
        seat_b = seats[1]
        seat_b.status = SeatStatus.AVAILABLE  # Reset ghế B về trống (để tránh lỗi Booked từ fixture)
        db.session.commit()

        selected_seats_input = [{"id": seat_b.id, "name": "Seat_B"}]

        # 3. THỰC THI (User nhấn nút thanh toán gửi API lên)
        success, _, _, _ = dao.process_seat_reservations_secure(
            user.id, session_id, showtime.id, selected_seats_input
        )

        assert success is True

        # 4. KIỂM TRA LOGIC TỰ NHẢ GHẾ
        seat_a_check = db.session.get(ShowtimeSeat, seat_a.id)
        seat_b_check = db.session.get(ShowtimeSeat, seat_b.id)

        # Ghế A phải bị hủy bỏ (nhả về Available) do user đã bỏ tick
        assert seat_a_check.status == SeatStatus.AVAILABLE
        assert seat_a_check.hold_session_id is None

        # Ghế B phải được giữ chỗ thành công do user vừa chọn
        assert seat_b_check.status == SeatStatus.RESERVED
        assert seat_b_check.hold_session_id == session_id
