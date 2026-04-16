import hashlib
import pytest
from flask import Flask
from datetime import datetime, timedelta, date
from movieapp import db, login_manager
from movieapp.models import (
    Cinema, User, Showtime, Movie, Genre, MovieFormat, Room, Province,
    TranslationType, Ticket, BookingStatus, ShowtimeSeat, SeatStatus,
    Booking, Seat, SeatType
)


def create_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.secret_key = '34y394yjsbdkjsdjksdh'
    app.config['PAGE_SIZE'] = 2
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager.init_app(app)
    from movieapp.index import register_routes
    register_routes(app)
    return app


# ==========================================
# CẤU HÌNH CORE - FIX LỖI DB & THÊM CLIENT
# ==========================================

@pytest.fixture(scope="function")
def test_app():
    """Tạo App và DB mới hoàn toàn cho mỗi hàm test."""
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def test_client(test_app):
    """Fixture dùng để giả lập trình duyệt gửi request."""
    return test_app.test_client()


@pytest.fixture(scope="function")
def test_session(test_app):
    """Fixture dùng để thao tác trực tiếp với Database."""
    return db.session


# ==========================================
# CÁC TẦNG DỮ LIỆU MẪU (Giữ nguyên logic của bạn)
# ==========================================

@pytest.fixture
def sample_basic_setup(test_session):
    p_hcm = Province(name="TP.HCM")
    p_hn = Province(name="Hà Nội")
    f2d = MovieFormat(name="2D")
    f3d = MovieFormat(name="3D")
    st_normal = SeatType(name="Thường", surcharge=0.0)
    st_vip = SeatType(name="VIP", surcharge=20000.0)

    test_session.add_all([p_hcm, p_hn, f2d, f3d, st_normal, st_vip])
    test_session.commit()

    return {
        "provinces": {"hcm": p_hcm, "hn": p_hn},
        "formats": {"2D": f2d, "3D": f3d},
        "seat_types": {"normal": st_normal, "vip": st_vip}
    }


@pytest.fixture
def sample_cinemas(test_session, sample_basic_setup):
    p_hcm = sample_basic_setup["provinces"]["hcm"]
    p_hn = sample_basic_setup["provinces"]["hn"]
    st_normal = sample_basic_setup["seat_types"]["normal"]
    st_vip = sample_basic_setup["seat_types"]["vip"]

    c1 = Cinema(name="CGV Tân Phú", address="HCM", province_id=p_hcm.id, map_url="hi")
    c2 = Cinema(name="CGV Crescent Mall", address="HCM", province_id=p_hcm.id, map_url="hi")
    c3 = Cinema(name="CGV Yên Lãng", address="Hà Nội", province_id=p_hn.id, map_url="hi")
    test_session.add_all([c1, c2, c3])
    test_session.commit()

    r1 = Room(name="Phòng 01", capacity=20, cinema_id=c1.id)
    r2 = Room(name="Phòng 02", capacity=20, cinema_id=c2.id)
    r3 = Room(name="Phòng 03", capacity=20, cinema_id=c3.id)
    test_session.add_all([r1, r2, r3])
    test_session.commit()

    seats = []
    for room in [r1, r2, r3]:
        for i in range(1, 4):
            s_type_id = st_vip.id if i == 2 else st_normal.id
            seats.append(Seat(room_id=room.id, seat_number=f"A0{i}", row="A", col=i, seat_type_id=s_type_id))
    test_session.add_all(seats)
    test_session.commit()

    return {
        **sample_basic_setup,
        "cinemas": {"cgv_tan_phu": c1, "cgv_crescent": c2, "cgv_yen_lang": c3},
        "rooms": [r1, r2, r3],
        "seats": seats
    }


@pytest.fixture
def sample_users(test_session):
    hashed_pwd = hashlib.md5("123456".encode('utf-8')).hexdigest()
    u1 = User(username="new_user1", email='user1@gmail.com', password=hashed_pwd)
    u2 = User(username="new_user2", email='user2@gmail.com', password=hashed_pwd)
    test_session.add_all([u1, u2])
    test_session.commit()
    return {"users": {"user1": u1, "user2": u2}}


@pytest.fixture
def sample_movies_data(test_session, sample_cinemas):
    g_action = Genre(name="Hành động")
    g_comedy = Genre(name="Hài hước")
    test_session.add_all([g_action, g_comedy])

    now = datetime.utcnow()
    m1 = Movie(name="Phim Hành Động Sắp Chiếu", release_date=now - timedelta(days=10), duration=120)
    m1.genres.append(g_action)
    m2 = Movie(name="Phim Hài Đã Chiếu", release_date=now - timedelta(days=20), duration=90)
    m2.genres.append(g_comedy)
    m3 = Movie(name="Phim Mới Nhập Kho", release_date=now + timedelta(days=30), duration=100)
    m3.genres.append(g_action)

    test_session.add_all([m1, m2, m3])
    test_session.commit()
    return {**sample_cinemas, "genres": {"action": g_action, "comedy": g_comedy},
            "movies": {"hot": m1, "old": m2, "new": m3}}


@pytest.fixture
def sample_showtimes_complex(test_session, sample_movies_data):
    f2d = sample_movies_data["formats"]["2D"]
    r1 = sample_movies_data["rooms"][0]
    m1 = sample_movies_data["movies"]["hot"]
    now = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=10)
    st1 = Showtime(movie_id=m1.id, room_id=r1.id, format_id=f2d.id, translation=TranslationType.SUBTITLE,
                   start_time=now, end_time=now + timedelta(hours=2), base_price=50000)
    test_session.add(st1)
    test_session.commit()
    sts_list = []
    room_1_seats = [s for s in sample_movies_data["seats"] if s.room_id == r1.id]
    for idx, seat in enumerate(room_1_seats):
        status = SeatStatus.BOOKED if idx == 0 else SeatStatus.AVAILABLE
        sts_list.append(ShowtimeSeat(showtime_id=st1.id, seat_id=seat.id, status=status,
                                     price=st1.base_price + seat.seat_type.surcharge))
    test_session.add_all(sts_list)
    test_session.commit()
    return {**sample_movies_data, "showtime": st1, "showtime_seats": sts_list}


@pytest.fixture
def sample_full_chain(test_session, sample_users, sample_showtimes_complex):
    u1 = sample_users["users"]["user1"]
    st1 = sample_showtimes_complex["showtime"]
    sts_target = sample_showtimes_complex["showtime_seats"][1]
    booking = Booking(user_id=u1.id, showtime_id=st1.id, total_price=sts_target.price, status=BookingStatus.PAID,
                      payment_method="MoMo")
    test_session.add(booking)
    test_session.commit()
    ticket = Ticket(booking_id=booking.id, showtime_seat_id=sts_target.id, final_price=sts_target.price,
                    is_checked_in=False)
    test_session.add(ticket)
    test_session.commit()
    return {**sample_users, **sample_showtimes_complex, "booking": booking, "ticket": ticket}


@pytest.fixture
def sample_provinces(test_session):
    p1 = Province(id=2, name="Hà Nội")
    p2 = Province(id=1, name="TPHCM")
    p3 = Province(id=3, name="Đà Nẵng")
    test_session.add_all([p1, p2, p3])
    test_session.commit()

    yield p1, p2, p3


@pytest.fixture
def sample_genres(test_session):
    g1 = Genre(id=1, name="Kinh dị")
    g2 = Genre(id=2, name="Hành động")
    g3 = Genre(id=3, name="Phiêu lưu")
    test_session.add_all([g1, g2, g3])
    test_session.commit()

    yield g1, g2, g3


@pytest.fixture
def sample_rooms(test_session, sample_cinemas):
    c1, c2, c3 = sample_cinemas
    r1 = Room(name="Phòng 1", cinema_id=c1.id)
    r2 = Room(name="Phòng 2", cinema_id=c2.id)
    test_session.add_all([r1, r2])
    test_session.commit()

    yield r1, r2


@pytest.fixture
def sample_movies(test_session):
    m1 = Movie(name="Lật Mặt 7", release_date=datetime(2024, 4, 26))
    m2 = Movie(name="Mai", release_date=datetime(2024, 2, 10))
    mf = MovieFormat(name="2D")
    test_session.add_all([m1, m2, mf])
    test_session.commit()
    yield m1, m2, mf


@pytest.fixture
def sample_showtime_data(test_session, sample_movies, sample_rooms, sample_cinemas):
    r1, r2 = sample_rooms
    m1, m2, mf = sample_movies
    c1, c2, c3 = sample_cinemas

    st1 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 4, 15, 10, 0),
                   end_time=datetime(2026, 4, 15, 12, 0), format_id=mf.id)
    st2 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 4, 15, 13, 0),
                   end_time=datetime(2026, 4, 15, 15, 0), format_id=mf.id)
    st3 = Showtime(movie_id=m2.id, room_id=r1.id, start_time=datetime(2026, 4, 15, 16, 0),
                   end_time=datetime(2026, 4, 15, 18, 0), format_id=mf.id)
    # Cùng rạp khác ngày
    st4 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 4, 16, 10, 0),
                   end_time=datetime(2026, 4, 16, 12, 0), format_id=mf.id)
    # Cùng ngày khác rạp
    st5 = Showtime(movie_id=m1.id, room_id=r2.id, start_time=datetime(2026, 4, 15, 20, 0),
                   end_time=datetime(2026, 4, 15, 22, 0), format_id=mf.id)
    test_session.add_all([st1, st2, st3, st4, st5])
    test_session.commit()
    return {
        "cinema_1_id": c1.id,
        "cinema_2_id": c2.id,
        "movie_1": m1,
        "movie_2": m2
    }


@pytest.fixture
def sample_users(test_session):
    user1 = User(username="testuser", email="test@gmail.com", password="123")
    user2 = User(username="dat", email="dat@gmail.com", password="123")
    test_session.add_all([user1, user2])
    test_session.commit()
    yield user1, user2


@pytest.fixture
def sample_seats(test_session, sample_rooms):
    r1, r2 = sample_rooms
    s1 = Seat(room_id=r1.id, seat_number="A1", row="A", col=1, seat_type_id=1)
    s2 = Seat(room_id=r1.id, seat_number="A2", row="A", col=2, seat_type_id=1)
    s3 = Seat(room_id=r1.id, seat_number="A3", row="A", col=3, seat_type_id=1)
    test_session.add_all([s1, s2, s3])
    test_session.commit()
    yield s1, s2, s3


@pytest.fixture
def sample_booking_data(test_session, sample_seats, sample_rooms, sample_users):
    r1, r2 = sample_rooms
    u1, u2 = sample_users
    st = Showtime(movie_id=1, room_id=r1.id, start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1),
                  format_id=1)
    test_session.add(st)
    test_session.commit()

    s1, s2, s3 = sample_seats
    st_seat1 = ShowtimeSeat(showtime_id=st.id, seat_id=s1.id, price=50000)
    st_seat2 = ShowtimeSeat(showtime_id=st.id, seat_id=s2.id, price=50000)
    st_seat3 = ShowtimeSeat(showtime_id=st.id, seat_id=s3.id, price=50000)
    test_session.add_all([st_seat1, st_seat2, st_seat3])
    test_session.commit()
    yield {
        "user_id": u1.id,
        "showtime_id": st.id,
        "seat1_id": str(st_seat1.id),
        "seat2_id": str(st_seat2.id),
        "seat3_id": str(st_seat3.id)
    }


@pytest.fixture
def sample_update_status(test_session, sample_rooms, sample_users, sample_movies, sample_seats):
    r1, r2 = sample_rooms
    u1, u2 = sample_users
    m1, m2, mf = sample_movies

    st = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1),
                  format_id=mf.id)
    test_session.add(st)
    test_session.flush()

    s1, s2, s3 = sample_seats
    session_id = "momo_session_123"
    expire_time = datetime.utcnow() + timedelta(minutes=10)

    st_seat = ShowtimeSeat(showtime_id=st.id, seat_id=s1.id, status=SeatStatus.RESERVED, hold_until=expire_time,
                           hold_session_id=session_id, price=50000)
    test_session.add(st_seat)
    test_session.flush()

    # Hóa đơn
    booking = Booking(user_id=u1.id, showtime_id=st.id, status=BookingStatus.PENDING, total_price=50000)
    test_session.add(booking)
    test_session.flush()

    ticket = Ticket(booking_id=booking.id, showtime_seat_id=st_seat.id, final_price=50000)
    test_session.add(ticket)
    test_session.commit()
    yield {
        "booking_id": booking.id,
        "st_seat_id": st_seat.id,
        "session_id": session_id
    }


@pytest.fixture
def sample_bookings_for_checkin(test_session, sample_rooms, sample_users, sample_movies):
    r1, r2 = sample_rooms
    m1, m2, mf = sample_movies
    u1, u2 = sample_users
    st1 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1),
                   format_id=mf.id)
    st2 = Showtime(movie_id=m2.id, room_id=r2.id, start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1),
                   format_id=mf.id)
    test_session.add_all([st1, st2])
    test_session.flush()

    b1 = Booking(user_id=u1.id, showtime_id=st1.id, total_price=50000, status=BookingStatus.PAID)
    b2 = Booking(user_id=u1.id, showtime_id=st2.id, total_price=50000, status=BookingStatus.PAID)
    b3 = Booking(user_id=u2.id, showtime_id=st2.id, total_price=50000, status=BookingStatus.PAID)
    b4 = Booking(user_id=u2.id, showtime_id=st1.id, total_price=50000, status=BookingStatus.PAID)
    test_session.add_all([b1, b2, b3, b4])
    test_session.commit()

    yield b1, b2, b3, b4
