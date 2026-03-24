import hashlib
import json
import os
from datetime import datetime

from movieapp import app, db
# Import đầy đủ Models, Enums và bảng movie_genre
from movieapp.models import (
    User, Genre, Movie, movie_genre, Cinema, Room,
    Seat, Showtime, ShowtimeSeat, Booking, Ticket,
    UserRole, SeatStatus, BookingStatus, TranslationType,
    Province, MovieFormat  # Thêm Province và MovieFormat
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

        # 2.1. Nạp Users
        for u in load_json("user.json"):
            u['role'] = UserRole(u['role'])
            u['password'] = hashlib.md5(u['password'].encode("utf-8")).hexdigest()
            db.session.add(User(**u))

        # 2.2. Nạp Genres
        for g in load_json("genre.json"):
            db.session.add(Genre(**g))

        # 2.3. Nạp Province (Phải có trước Cinema)
        for p in load_json("province.json"):
            db.session.add(Province(**p))

        # 2.4. Nạp MovieFormat (Phải có trước Showtime)
        for mf in load_json("movie_format.json"):
            db.session.add(MovieFormat(**mf))

        db.session.commit()

        # 2.5. Nạp Cinemas
        for c in load_json("cinema.json"):
            db.session.add(Cinema(**c))

        db.session.commit()

        # 2.6. Nạp Movies
        for m in load_json("movie.json"):
            # Lấy ngày chuẩn (bỏ giờ phút giây) vì CSDL là kiểu Date
            m['release_date'] = datetime.strptime(m['release_date'], "%Y-%m-%d").date()
            db.session.add(Movie(**m))

        db.session.commit()

        # 2.7. Nạp Rooms
        for r in load_json("room.json"):
            db.session.add(Room(**r))

        db.session.commit()

        # 2.8. Nạp Bảng trung gian Movie_Genre
        for mg in load_json("movie_genre.json"):
            # Bỏ qua id, chỉ lấy movie_id và genre_id
            stmt = movie_genre.insert().values(movie_id=mg['movie_id'], genre_id=mg['genre_id'])
            db.session.execute(stmt)

        # 2.9. Nạp Seats
        for s in load_json("seat.json"):
            db.session.add(Seat(**s))

        db.session.commit()

        # 2.10. Nạp Showtimes
        for st in load_json("showtime.json"):
            # Chú ý chữ 'T' trong format thời gian
            st['start_time'] = datetime.strptime(st['start_time'], "%Y-%m-%dT%H:%M:%S")
            st['end_time'] = datetime.strptime(st['end_time'], "%Y-%m-%dT%H:%M:%S")
            st['translation'] = TranslationType(st['translation'])  # Ép kiểu Enum
            db.session.add(Showtime(**st))

        db.session.commit()

        # 2.11. Nạp ShowtimeSeats (Lưu ý tên file: showtime_seat.json)
        for ss in load_json("showtime_seat.json"):
            ss['status'] = SeatStatus(ss['status'])
            db.session.add(ShowtimeSeat(**ss))

        db.session.commit()

        # 2.12. Nạp Bookings
        for b in load_json("booking.json"):
            b['status'] = BookingStatus(b['status'])
            db.session.add(Booking(**b))

        db.session.commit()

        # 2.13. Nạp Tickets
        for t in load_json("ticket.json"):
            db.session.add(Ticket(**t))

        db.session.commit()

        print("ĐÃ SEED DỮ LIỆU THÀNH CÔNG!")