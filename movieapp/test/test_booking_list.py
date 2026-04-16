import pytest
from movieapp import dao, db
from movieapp.models import Booking
# Sử dụng các fixture từ test_base.py
from movieapp.test.test_base import (
    test_app, test_session, sample_users, sample_showtimes_complex, sample_movies_data, sample_cinemas,
    sample_basic_setup
)


# Test phân trang (Trang 1 và Trang 2)
def test_get_bookings_pagination_with_base_data(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        st = sample_showtimes_complex["showtime"]

        # Tạo 3 booking để test với PAGE_SIZE = 2
        for i in range(3):
            db.session.add(Booking(user_id=user.id, showtime_id=st.id, total_price=100 + i))
        db.session.commit()

        # Kiểm tra trang 1: Phải có đúng 2 bản ghi
        page1 = dao.get_bookings_by_user(user.id, page=1)
        assert len(page1) == 2

        # Kiểm tra trang 2: Phải có 1 bản ghi còn lại
        page2 = dao.get_bookings_by_user(user.id, page=2)
        assert len(page2) == 1


#  Test sắp xếp mới nhất lên đầu (Order By Desc)
def test_get_bookings_order_desc(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        st = sample_showtimes_complex["showtime"]

        # Booking b1 tạo trước, b2 tạo sau
        b1 = Booking(user_id=user.id, showtime_id=st.id, total_price=500)
        db.session.add(b1)
        db.session.flush()

        b2 = Booking(user_id=user.id, showtime_id=st.id, total_price=999)
        db.session.add(b2)
        db.session.commit()

        bookings = dao.get_bookings_by_user(user.id, page=1)

        # Đơn hàng b2 (999) phải nằm ở vị trí đầu tiên
        assert bookings[0].total_price == 999


# Test trường hợp page=None (Lấy tất cả không phân trang)
def test_get_bookings_no_pagination(test_app, sample_users, sample_showtimes_complex):
    with test_app.app_context():
        user = sample_users["users"]["user1"]
        st = sample_showtimes_complex["showtime"]

        # Tạo 3 booking
        for i in range(3):
            db.session.add(Booking(user_id=user.id, showtime_id=st.id, total_price=i))
        db.session.commit()

        all_bookings = dao.get_bookings_by_user(user.id, page=None)
        assert len(all_bookings) == 3


# Test User không tồn tại hoặc không có đơn hàng
def test_get_bookings_user_empty(test_app):
    with test_app.app_context():
        bookings = dao.get_bookings_by_user(user_id=9999)
        assert bookings == []
