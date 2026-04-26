from movieapp import dao, db
from movieapp.models import SeatStatus


# LẤY GIỎ HÀNG THÀNH CÔNG KHI CÓ GHẾ ĐANG GIỮ
def test_get_user_reserved_seats_session_success(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        showtime = sample_showtimes_complex["showtime"]

        # Merge ghế thứ 2 vào session hiện tại để chỉnh sửa
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][1])

        # User 1 đang giữ ghế này
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = user.id
        db.session.commit()

        # Thực thi hàm
        result = dao.get_user_reserved_seats_session(user.id, showtime.id)

        # Kiểm tra kết quả
        seat_id_str = str(st_seat.id)

        assert len(result) == 1
        assert seat_id_str in result

        # Kiểm tra cấu trúc dữ liệu trả về có chuẩn form chưa
        assert result[seat_id_str]["id"] == seat_id_str
        assert result[seat_id_str]["name"] == f"{st_seat.seat.row}{st_seat.seat.col}"
        assert result[seat_id_str]["price"] == float(st_seat.price)


# TRẢ VỀ GIỎ HÀNG RỖNG KHI KHÔNG CÓ GHẾ NÀO
def test_get_user_reserved_seats_session_empty(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user2"]  # Dùng user2 chưa mua ghế nào
        showtime = sample_showtimes_complex["showtime"]

        # Thực thi hàm
        result = dao.get_user_reserved_seats_session(user.id, showtime.id)

        assert result == {}


# XỬ LÝ ÊM ÁI KHI GIÁ TRỊ 'PRICE' LÀ NONE
def test_get_user_reserved_seats_session_price_none(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        showtime = sample_showtimes_complex["showtime"]
        st_seat = db.session.merge(sample_showtimes_complex["showtime_seats"][2])

        # User 1 giữ ghế, NHƯNG hệ thống bị lỗi dữ liệu khiến price bị None
        st_seat.status = SeatStatus.RESERVED
        st_seat.hold_session_id = user.id
        st_seat.price = None
        db.session.commit()

        # Thực thi hàm
        result = dao.get_user_reserved_seats_session(user.id, showtime.id)

        seat_id_str = str(st_seat.id)
        assert result[seat_id_str]["price"] == 0.0
