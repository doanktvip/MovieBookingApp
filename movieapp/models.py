from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from movieapp import db, app
from flask_login import UserMixin
from datetime import datetime
import enum
from datetime import timedelta


# --- 1. Lớp Base ---
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Dùng utcnow để đồng bộ
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- 2. Các Enum ---
class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class SeatStatus(enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    RESERVED = "reserved"


class BookingStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TranslationType(enum.Enum):
    SUBTITLE = "Phụ đề"
    DUBBING = "Lồng tiếng"


movie_genre = db.Table('movie_genre',
                       Column('movie_id', Integer, ForeignKey('movie.id'), primary_key=True),
                       Column('genre_id', Integer, ForeignKey('genre.id'), primary_key=True))


# --- 3. Định nghĩa các Model ---
class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    active = Column(Boolean, default=True)
    tickets=relationship('Ticket', backref='user', lazy=True)
    bookings = relationship('Booking', backref='user', lazy=True)


class Genre(BaseModel):
    __tablename__ = 'genre'
    name = Column(String(50), nullable=False)
    movies = relationship('Movie', secondary=movie_genre, back_populates='genres', lazy=True)


class Movie(BaseModel):
    __tablename__ = 'movie'
    title = Column(String(255), nullable=False)
    duration = Column(Integer)
    image = Column(String(255))
    description = Column(Text)
    release_date = Column(DateTime, nullable=False)
    rate = Column(Float)
    limited_age = Column(Integer)
    is_active = Column(Boolean, default=True)
    showtimes = relationship('Showtime', backref='movie', lazy=True)
    genres = relationship('Genre', secondary=movie_genre, back_populates='movies', lazy=True)


class Room(BaseModel):
    __tablename__ = 'room'
    room_name = Column(String(50), nullable=False)
    capacity = Column(Integer)
    cinema_id = Column(Integer, ForeignKey('cinema.id'), nullable=False)

    seats = relationship('Seat', backref='room', cascade="all, delete-orphan", lazy=True)
    showtimes = relationship('Showtime', backref='room', lazy=True)


class Seat(BaseModel):
    __tablename__ = 'seat'
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    seat_number = Column(String(10), nullable=False)
    row = Column(String(2))
    col = Column(Integer)
    is_vip = Column(Boolean, default=False)

    seat_type_id = Column(Integer, ForeignKey('seat_type.id'), nullable=False)


class SeatType(BaseModel):
    __tablename__ = 'seat_type'
    name = Column(String(50), nullable=False)
    surcharge = Column(Float, default=0.0)

    seats = relationship('Seat', backref='seat_type', lazy=True)


class MovieFormat(BaseModel):
    __tablename__ = 'movie_format'
    name = Column(String(20), nullable=False, unique=True)

    showtimes = relationship('Showtime', backref='movie_format', lazy=True)


class Showtime(BaseModel):
    __tablename__ = 'showtime'
    movie_id = Column(Integer, ForeignKey('movie.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    base_price = Column(Float, default=0.0)

    format_id = Column(Integer, ForeignKey('movie_format.id'), nullable=False)
    translation = Column(Enum(TranslationType), default=TranslationType.SUBTITLE)
    bookings = relationship('Booking', backref='showtime', lazy=True)
    showtime_seats = relationship('ShowtimeSeat', backref='showtime', cascade="all, delete-orphan", lazy=True)


class ShowtimeSeat(BaseModel):
    __tablename__ = 'showtime_seat'
    showtime_id = Column(Integer, ForeignKey('showtime.id'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE)
    price = Column(Float)
    hold_until = Column(DateTime, nullable=True)
    hold_session_id = Column(String(255), nullable=True)

    ticket = relationship('Ticket', backref='showtime_seat', uselist=False, lazy=True)
    seat = relationship('Seat', backref='showtime_seats', lazy=True)


class Booking(BaseModel):
    __tablename__ = 'booking'
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    showtime_id = Column(Integer, ForeignKey('showtime.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    payment_method = Column(String(50))
    transaction_id = Column(String(100), nullable=True)

    tickets = relationship('Ticket', backref='booking', cascade="all, delete-orphan", lazy=True)


class Ticket(BaseModel):
    __tablename__ = 'ticket'
    user_id=Column(Integer, ForeignKey('user.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    showtime_seat_id = Column(Integer, ForeignKey('showtime_seat.id'), nullable=False)
    final_price = Column(Float, nullable=False)
    is_checked_in = Column(Boolean, default=False)


class Cinema(BaseModel):
    __tablename__ = 'cinema'
    name = Column(String(50), nullable=False)
    address = Column(String(200), nullable=False)
    map_url = Column(String(200), nullable=False)
    hotline = Column(String(20))
    rooms = relationship('Room', backref='cinema', lazy=True)
    province_id = Column(Integer, ForeignKey('province.id'), nullable=False)


class Province(BaseModel):
    __tablename__ = 'province'
    name = Column(String(50), nullable=False)
    cinemas = relationship('Cinema', backref='province', lazy=True)
