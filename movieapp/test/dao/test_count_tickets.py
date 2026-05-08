from movieapp import dao, db
from movieapp.models import Booking, Ticket, BookingStatus


# Đầu vào bị None hoặc rỗng
def test_count_tickets_invalid_inputs(test_app):
    with test_app.app_context():
        assert dao.count_user_tickets_for_showtime(None, 1) == 0
        assert dao.count_user_tickets_for_showtime(1, None) == 0
        assert dao.count_user_tickets_for_showtime(None, None) == 0


# Khách hàng chưa mua vé nào cho suất chiếu này
def test_count_tickets_no_booking(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user2 = sample_users["users"]["user2"]  # user2 chưa mua gì
        showtime = sample_showtimes_complex["showtime"]

        # Số vé phải là 0
        assert dao.count_user_tickets_for_showtime(user2.id, showtime.id) == 0

        # Test thêm: user1 kiểm tra 1 suất chiếu ảo
        user1 = sample_users["users"]["user1"]
        assert dao.count_user_tickets_for_showtime(user1.id, 9999) == 0


# Đếm chính xác các vé đang PENDING và PAID
def test_count_tickets_valid_status(test_app, sample_full_chain):
    with test_app.app_context():
        user1 = sample_full_chain["users"]["user1"]
        showtime = sample_full_chain["showtime"]

        # sample_full_chain đã cho sẵn user1 1 vé PAID
        count_initial = dao.count_user_tickets_for_showtime(user1.id, showtime.id)
        assert count_initial == 1

        # Giả lập User 1 đang chọn thêm 1 ghế và đang chờ thanh toán (PENDING)
        sts_pending = sample_full_chain["showtime_seats"][2]
        booking_pending = Booking(
            user_id=user1.id,
            showtime_id=showtime.id,
            total_price=sts_pending.price,
            status=BookingStatus.PENDING
        )
        db.session.add(booking_pending)
        db.session.flush()

        ticket_pending = Ticket(booking_id=booking_pending.id, showtime_seat_id=sts_pending.id,
                                final_price=sts_pending.price)
        db.session.add(ticket_pending)
        db.session.commit()

        # Lúc này tổng số vé phải được cộng lên thành 2 (1 PAID + 1 PENDING)
        count_after = dao.count_user_tickets_for_showtime(user1.id, showtime.id)
        assert count_after == 2


# Vé CANCELLED và FAILED không được đếm vào tổng vé
def test_count_tickets_ignore_failed_cancelled(test_app, sample_full_chain):
    with test_app.app_context():
        user1 = sample_full_chain["users"]["user1"]
        showtime = sample_full_chain["showtime"]

        # Thêm 1 đơn hàng bị FAILED (Thanh toán thất bại)
        b_failed = Booking(user_id=user1.id, showtime_id=showtime.id, total_price=100, status=BookingStatus.FAILED)
        db.session.add(b_failed)
        db.session.flush()
        db.session.add(
            Ticket(booking_id=b_failed.id, showtime_seat_id=sample_full_chain["showtime_seats"][0].id, final_price=100))

        # Thêm 1 đơn hàng bị CANCELLED (Khách hủy vé)
        b_cancel = Booking(user_id=user1.id, showtime_id=showtime.id, total_price=100, status=BookingStatus.CANCELLED)
        db.session.add(b_cancel)
        db.session.flush()
        db.session.add(
            Ticket(booking_id=b_cancel.id, showtime_seat_id=sample_full_chain["showtime_seats"][2].id, final_price=100))

        db.session.commit()

        # Tổng vé đếm được vẫn chỉ là 1 (từ vé PAID trong sample_full_chain)
        # Các vé Failed và Cancelled đã bị bỏ qua
        assert dao.count_user_tickets_for_showtime(user1.id, showtime.id) == 1
