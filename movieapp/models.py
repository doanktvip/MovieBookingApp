import json

from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from movieapp import db, app
from flask_login import UserMixin
from datetime import datetime
import enum


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


# --- 3. Định nghĩa các Model ---
class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    active = Column(Boolean, default=True)

    bookings = relationship('Booking', backref='user', lazy=True)

class Genre(BaseModel):
    __tablename__ = 'genre'
    name=Column(String(50), nullable=False)

class MovieGenre(BaseModel):
    __tablename__ = 'movie_genre'
    movie_id = Column(Integer, ForeignKey('movie.id'), nullable=False)
    genre_id = Column(Integer, ForeignKey('genre.id'), nullable=False)

class Movie(BaseModel):
    __tablename__ = 'movie'
    title = Column(String(255), nullable=False)
    duration = Column(Integer)
    image = Column(String(255))
    description = Column(Text)
    release_date = Column(DateTime)
    rate=Column(Float)
    limited_age=Column(Integer)
    is_active = Column(Boolean, default=True)
    showtimes = relationship('Showtime', backref='movie', lazy=True)
    genres = relationship('Genre',secondary="movie_genre", backref='movie', lazy=True)


class Room(BaseModel):
    __tablename__ = 'room'
    room_name = Column(String(50), nullable=False)
    capacity = Column(Integer)

    seats = relationship('Seat', backref='room', cascade="all, delete-orphan", lazy=True)
    showtimes = relationship('Showtime', backref='room', lazy=True)


class Seat(BaseModel):
    __tablename__ = 'seat'
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    seat_number = Column(String(10), nullable=False)
    row = Column(String(2))
    col = Column(Integer)
    is_vip = Column(Boolean, default=False)


class Showtime(BaseModel):
    __tablename__ = 'showtime'
    movie_id = Column(Integer, ForeignKey('movie.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    base_price = Column(Float, default=0.0)

    showtime_seats = relationship('ShowtimeSeat', backref='showtime', lazy=True)


class ShowtimeSeat(BaseModel):
    __tablename__ = 'showtime_seat'
    showtime_id = Column(Integer, ForeignKey('showtime.id'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE)
    actual_price = Column(Float)


class Booking(BaseModel):
    __tablename__ = 'booking'
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    showtime_id = Column(Integer, ForeignKey('showtime.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    payment_method = Column(String(50))

    tickets = relationship('Ticket', backref='booking', lazy=True)


class Ticket(BaseModel):
    __tablename__ = 'ticket'
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    price = Column(Float)


