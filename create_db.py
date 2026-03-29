import hashlib
import json
import os
from datetime import datetime
from tkinter.font import names

import movieapp.dao
from movieapp import app, db
# Import đầy đủ Models, Enums và bảng movie_genre
from movieapp.models import (
    User, Genre, Movie, movie_genre, Cinema, Room,
    Seat, Showtime, ShowtimeSeat, Booking, Ticket,
    UserRole, SeatStatus, BookingStatus, TranslationType,
    Province, MovieFormat, SeatType
)


# Hàm hỗ trợ đọc file JSON
def load_json(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'movieapp', 'data', filename)
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    with app.app_context():
        # 1. Xóa và tạo lại toàn bộ bảng
        db.drop_all()
        print("--- Đã xóa sạch các bảng cũ ---")
        db.create_all()
        print("--- Đã tạo các bảng mới thành công! ---")

        # 2. Bắt đầu nạp dữ liệu theo thứ tự (Tránh lỗi Khóa ngoại)

        try:
            # 2.1. Nạp Users
            for u in load_json("user.json"):
                u['role'] = UserRole(u['role'].lower())  # Ép về chữ thường cho an toàn
                u['password'] = hashlib.md5(u['password'].encode("utf-8")).hexdigest()
                db.session.add(User(**u))

            # 2.2. Nạp Genres
            for g in load_json("genre.json"):
                db.session.add(Genre(**g))

            # 2.3. Nạp Province
            for p in load_json("province.json"):
                db.session.add(Province(**p))

            # 2.4. Nạp MovieFormat
            for mf in load_json("movie_format.json"):
                db.session.add(MovieFormat(**mf))

            db.session.commit()

            # 2.5. Nạp Cinemas
            for c in load_json("cinema.json"):
                db.session.add(Cinema(**c))

            db.session.commit()

            # 2.6. Nạp Movies
            for m in load_json("movie.json"):
                # SỬA Ở ĐÂY: Bỏ .date() đi để giữ nguyên kiểu DateTime cho khớp với Model
                m['release_date'] = datetime.strptime(m['release_date'], "%Y-%m-%d")
                db.session.add(Movie(**m))

            db.session.commit()

            # 2.7. Nạp Rooms
            for r in load_json("room.json"):
                db.session.add(Room(**r))

            db.session.commit()

            # 2.8. Nạp Bảng trung gian Movie_Genre
            for mg in load_json("movie_genre.json"):
                stmt = movie_genre.insert().values(movie_id=mg['movie_id'], genre_id=mg['genre_id'])
                db.session.execute(stmt)

            # 2.9. Nạp Seat Type
            seat_type_normal = SeatType(name="Normal", surcharge=0)
            seat_type_vip = SeatType(name="Vip", surcharge=20000)
            db.session.add_all([seat_type_normal, seat_type_vip])
            db.session.commit()

            # 2.10. Nạp Seats
            name_row = ["A", "B", "C", "D", "E", "F", "G", "H"]
            for i in name_row:
                for j in range(1, 9):
                    s = Seat(room_id=1, seat_number=f"{i}{j}", row=i, col=j, seat_type_id=1)
                    if i in ["G", "H"]:
                        s.is_vip = True
                        s.seat_type_id = 2
                    db.session.add(s)
            db.session.commit()

            # 2.11. Nạp Showtimes
            for st in load_json("showtime.json"):
                st['start_time'] = datetime.strptime(st['start_time'], "%Y-%m-%dT%H:%M:%S")
                st['end_time'] = datetime.strptime(st['end_time'], "%Y-%m-%dT%H:%M:%S")
                st['translation'] = TranslationType(st['translation'])
                db.session.add(Showtime(**st))

            db.session.commit()

            # 2.12. Nạp ShowtimeSeats (Đảm bảo file tên là showtime_seat.json)
            seats = movieapp.dao.get_seats_all()
            for s in seats:
                showtime_seat = ShowtimeSeat(seat_id=s.id, showtime_id=1, price=50000)
                db.session.add(showtime_seat)
            db.session.commit()

            # 2.13. Nạp Bookings
            if os.path.exists(os.path.join(os.path.dirname(__file__), 'movieapp', 'data', 'booking.json')):
                for b in load_json("booking.json"):
                    b['status'] = BookingStatus(b['status'].lower())
                    db.session.add(Booking(**b))
                db.session.commit()

            # 2.14. Nạp Tickets
            if os.path.exists(os.path.join(os.path.dirname(__file__), 'movieapp', 'data', 'ticket.json')):
                for t in load_json("ticket.json"):
                    db.session.add(Ticket(**t))
                db.session.commit()

            print("ĐÃ SEED DỮ LIỆU THÀNH CÔNG!")

        except Exception as e:
            db.session.rollback()
            print(f"CÓ LỖI XẢY RA KHI SEED DỮ LIỆU: {e}")
