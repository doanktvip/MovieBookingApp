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
    test_session.add(booking);
    test_session.commit()
    ticket = Ticket(booking_id=booking.id, showtime_seat_id=sts_target.id, final_price=sts_target.price,
                    is_checked_in=False)
    test_session.add(ticket)
    test_session.commit()
    return {**sample_users, **sample_showtimes_complex, "booking": booking, "ticket": ticket}
