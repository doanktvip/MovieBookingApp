from datetime import datetime, timedelta

import pytest
from flask import Flask
from movieapp import db
from movieapp.models import Cinema, Province, Genre, Room, Movie, MovieFormat, Showtime, User, Seat, ShowtimeSeat, \
    SeatStatus, Booking, BookingStatus, Ticket


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)

    return app

@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def sample_cinemas(test_session):
    c1=Cinema(name="CGV Tân Phú",address="30 Tân Thắng, Sơn Kỳ, Quận Tân Phú, TP.HCM",province_id=1,map_url="hi")
    c2 = Cinema(name="CGV Crescent Mall", address="12 Tôn Dật Tiên, Phú Mỹ Hưng, TP.HCM", province_id=1, map_url="hi")
    c3 = Cinema(name="CGV Yên Lãng", address="120 Yên Lãng, Quận Hà Tây, Hà Nội", province_id=2, map_url="hi")
    test_session.add_all([c1,c2,c3])
    test_session.commit()

    yield c1,c2,c3

@pytest.fixture
def sample_provinces(test_session):
    p1=Province(id=2,name="Hà Nội")
    p2=Province(id=1,name="TPHCM")
    p3=Province(id=3,name="Đà Nẵng")
    test_session.add_all([p1,p2,p3])
    test_session.commit()

    yield p1,p2,p3

@pytest.fixture
def sample_genres(test_session):
    g1=Genre(id=1,name="Kinh dị")
    g2=Genre(id=2,name="Hành động")
    g3=Genre(id=3,name="Phiêu lưu")
    test_session.add_all([g1,g2,g3])
    test_session.commit()

    yield g1,g2,g3

@pytest.fixture
def sample_rooms(test_session,sample_cinemas):
    c1, c2, c3 = sample_cinemas
    r1 = Room(name="Phòng 1", cinema_id=c1.id)
    r2 = Room(name="Phòng 2", cinema_id=c2.id)
    test_session.add_all([r1,r2])
    test_session.commit()

    yield r1,r2

@pytest.fixture
def sample_movies(test_session):
    m1 = Movie(name="Lật Mặt 7", release_date=datetime(2024, 4, 26))
    m2 = Movie(name="Mai", release_date=datetime(2024, 2, 10))
    mf = MovieFormat(name="2D")
    test_session.add_all([m1, m2, mf])
    test_session.commit()
    yield m1,m2,mf

@pytest.fixture
def sample_showtime_data(test_session,sample_movies,sample_rooms,sample_cinemas):
    r1,r2 = sample_rooms
    m1,m2,mf = sample_movies
    c1,c2,c3 = sample_cinemas

    st1 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 4, 15, 10, 0),
                   end_time=datetime(2026, 4, 15, 12, 0), format_id=mf.id)
    st2 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 4, 15, 13, 0),
                   end_time=datetime(2026, 4, 15, 15, 0), format_id=mf.id)
    st3 = Showtime(movie_id=m2.id, room_id=r1.id, start_time=datetime(2026, 4, 15, 16, 0),
                   end_time=datetime(2026, 4, 15, 18, 0), format_id=mf.id)
    # Cùng rạp khác ngày
    st4 = Showtime(movie_id=m1.id, room_id=r1.id, start_time=datetime(2026, 4, 16, 10, 0),
                   end_time=datetime(2026, 4, 16, 12, 0), format_id=mf.id)
    #Cùng ngày khác rạp
    st5 = Showtime(movie_id=m1.id, room_id=r2.id, start_time=datetime(2026, 4, 15, 20, 0),
                   end_time=datetime(2026, 4, 15, 22, 0), format_id=mf.id)
    test_session.add_all([st1,st2,st3,st4,st5])
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
    test_session.add_all([user1,user2])
    test_session.commit()
    yield user1,user2

@pytest.fixture
def sample_seats(test_session,sample_rooms):
    r1,r2=sample_rooms
    s1 = Seat(room_id=r1.id, seat_number="A1", row="A", col=1, seat_type_id=1)
    s2 = Seat(room_id=r1.id, seat_number="A2", row="A", col=2, seat_type_id=1)
    s3 = Seat(room_id=r1.id, seat_number="A3", row="A", col=3, seat_type_id=1)
    test_session.add_all([s1, s2, s3])
    test_session.commit()
    yield s1,s2,s3

@pytest.fixture
def sample_booking_data(test_session,sample_seats,sample_rooms,sample_users):
    r1,r2=sample_rooms
    u1,u2=sample_users
    st = Showtime(movie_id=1, room_id=r1.id, start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1), format_id=1)
    test_session.add(st)
    test_session.commit()

    s1,s2,s3 = sample_seats
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
def sample_update_status(test_session,sample_rooms,sample_users,sample_movies,sample_seats):
    r1,r2=sample_rooms
    u1,u2=sample_users
    m1,m2,mf = sample_movies

    st=Showtime(movie_id=m1.id, room_id=r1.id,start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1), format_id=mf.id)
    test_session.add(st)
    test_session.flush()

    s1,s2,s3 = sample_seats
    session_id = "momo_session_123"
    expire_time = datetime.utcnow() + timedelta(minutes=10)

    st_seat=ShowtimeSeat(showtime_id=st.id, seat_id=s1.id, status=SeatStatus.RESERVED,hold_until=expire_time,hold_session_id=session_id,price=50000)
    test_session.add(st_seat)
    test_session.flush()

    #Hóa đơn
    booking=Booking(user_id=u1.id,showtime_id=st.id,status=BookingStatus.PENDING,total_price=50000)
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
def sample_bookings_for_checkin(test_session,sample_rooms,sample_users,sample_movies):
    r1,r2=sample_rooms
    m1,m2,mf = sample_movies
    u1,u2=sample_users
    st1 = Showtime(movie_id=m1.id, room_id=r1.id,start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1), format_id=mf.id)
    st2 = Showtime(movie_id=m2.id, room_id=r2.id,start_time=datetime(2026, 5, 1), end_time=datetime(2026, 5, 1), format_id=mf.id)
    test_session.add_all([st1, st2])
    test_session.flush()

    b1=Booking(user_id=u1.id, showtime_id=st1.id, total_price=50000, status=BookingStatus.PAID)
    b2 = Booking(user_id=u1.id, showtime_id=st2.id, total_price=50000, status=BookingStatus.PAID)
    b3 = Booking(user_id=u2.id, showtime_id=st2.id, total_price=50000, status=BookingStatus.PAID)
    b4 = Booking(user_id=u2.id, showtime_id=st1.id, total_price=50000, status=BookingStatus.PAID)
    test_session.add_all([b1, b2, b3, b4])
    test_session.commit()

    yield b1, b2, b3, b4