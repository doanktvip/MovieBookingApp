import pytest
from sqlalchemy.exc import IntegrityError
from movieapp.test.conftest import test_session
from movieapp.models import User, Genre, Movie, Seat, Showtime, Booking, Cinema, ShowtimeSeat
from datetime import datetime


# --- 1. TEST RÀNG BUỘC (CONSTRAINTS) ---

def test_duplicate_username(test_session):
    """Kiểm tra ràng buộc UNIQUE cho username"""
    u1 = User(username="testuser", email="test1@gmail.com", password="123")
    test_session.add(u1)
    test_session.commit()

    u2 = User(username="testuser", email="test2@gmail.com", password="123")
    test_session.add(u2)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


def test_user_email_not_null(test_session):
    """Kiểm tra ràng buộc NOT NULL cho email"""
    u = User(username="no_email", password="123")  # Không có email
    test_session.add(u)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


def test_movie_name_not_null(test_session):
    """Kiểm tra ràng buộc NOT NULL cho tên phim"""
    m = Movie(release_date=datetime.now())  # Thiếu name
    test_session.add(m)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


# 2. Test hàm trả về name

def test_basemodel_str_on_genre(test_session):
    genre = Genre(name="Kinh dị")
    # Khi gọi str(genre), nó sẽ thực thi dòng 17 trong BaseModel
    assert str(genre) == "Kinh dị"


def test_basemodel_str_on_moviet(test_session):
    movie = Movie(name="Lật Mặt 7")
    assert str(movie) == "Lật Mặt 7"


def test_basemodel_str_on_cinema(test_session):
    cinema = Cinema(name="CGV Hùng Vương")
    assert str(cinema) == "CGV Hùng Vương"


def test_basemodel_str_on_user_override(test_session):
    """
    Lưu ý: Lớp User ghi đè (override) phương thức __str__ để trả về self.username thay vì self.name của BaseModel
    """
    user = User(username="nguyendoan", email="doan@ou.edu.vn")
    assert str(user) == "nguyendoan"


def test_basemodel_str_attribute_error(test_session):
    """
    model kế thừa BaseModel mà không có 'name' và không ghi đè __str__ thì văng lỗi AttributeError.
    """
    # Giả sử lớp Seat không có 'name' mà chỉ có 'seat_number'
    from movieapp.models import Seat
    seat = Seat(seat_number="A10")

    with pytest.raises(AttributeError):
        # Seat kế thừa BaseModel nhưng không có thuộc tính .name
        print(str(seat))


# Dòng 136-141
def test_showtime_str_with_start_time(test_session):
    """Kiểm tra hiển thị Showtime khi có thời gian bắt đầu"""
    m = Movie(name="Avatar 2", release_date=datetime.now())
    test_session.add(m)
    test_session.flush()  # Để lấy movie.name

    start = datetime(2023, 12, 25, 19, 30)
    st = Showtime(movie=m, start_time=start)

    expected = "Suất chiếu 19:30 25/12/2023 - Phim Avatar 2"
    assert str(st) == expected


def test_showtime_str_without_start_time(test_session):
    """Kiểm tra hiển thị Showtime khi start_time là None"""
    m = Movie(name="Dune", release_date=datetime.now())
    st = Showtime(movie=m, start_time=None)

    assert "Chưa xác định" in str(st)
    assert "Phim Dune" in str(st)


# Dòng 157-164
def test_showtime_seat_str_full_data(test_session):
    """Kiểm tra ShowtimeSeat khi có đầy đủ thông tin Ghế và Suất chiếu"""
    m = Movie(name="Iron Man", release_date=datetime.now())
    start = datetime(2023, 10, 10, 20, 0)
    st = Showtime(movie=m, start_time=start)
    seat = Seat(seat_number="H12")

    sts = ShowtimeSeat(showtime=st, seat=seat)

    expected = "Ghế H12 - Suất 20:00 10/10/2023"
    assert str(sts) == expected


def test_showtime_seat_str_missing_data(test_session):
    """Kiểm tra ShowtimeSeat khi thiếu thông tin"""
    # Trường hợp không có seat và showtime
    sts = ShowtimeSeat(showtime=None, seat=None)

    expected = "Ghế Trống - Suất Chưa xác định"
    assert str(sts) == expected


# Dòng 179-181
def test_booking_str_with_user(test_session):
    """Kiểm tra hiển thị Booking khi có User liên kết"""
    u = User(username="nguyenvana", email="a@gmail.com", password="123")
    test_session.add(u)

    b = Booking(id=100, user=u, total_price=50000.0, showtime_id=1)
    test_session.add(b)  # Thêm booking vào session
    test_session.flush()  # Flush để DB ghi nhận quan hệ

    expected = "Đơn #100 - Khách: nguyenvana"
    assert str(b) == expected


def test_booking_str_without_user(test_session):
    """Kiểm tra hiển thị Booking khi User bị None"""
    b = Booking(id=999, user=None, total_price=0.0)

    assert str(b) == "Đơn #999"
