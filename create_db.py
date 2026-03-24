import json
import os
from datetime import datetime

from movieapp import app, db
# Import tất cả Models, Enums và bảng movie_genre
from movieapp.models import (
    User, Genre, Movie, movie_genre, Cinema, Room,
    Seat, Showtime, ShowtimeSeat, Booking, Ticket,
    UserRole, SeatStatus, BookingStatus
)


# Hàm hỗ trợ đọc file JSON
def load_json(filename):
    # Đảm bảo đường dẫn chính xác (bạn có thể điều chỉnh tùy cấu trúc thư mục)
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

        # 2. Bắt đầu nạp dữ liệu theo thứ tự (Tránh lỗi Khóa ngoại - Foreign Key)

        # 2.1. Nạp Users
        for u in load_json("user.json"):
            u['role'] = UserRole(u['role'])  # Chuyển string thành Enum
            db.session.add(User(**u))

        # 2.2. Nạp Genres
        for g in load_json("genre.json"):
            db.session.add(Genre(**g))

        # 2.3. Nạp Cinemas
        for c in load_json("cinema.json"):
            db.session.add(Cinema(**c))

        db.session.commit()  # Lưu lại để lấy ID cho các bảng sau

        # 2.4. Nạp Movies (Cần xử lý datetime)
        for m in load_json("movie.json"):
            m['release_date'] = datetime.strptime(m['release_date'], "%Y-%m-%d")
            db.session.add(Movie(**m))

        # 2.5. Nạp Rooms
        for r in load_json("room.json"):
            db.session.add(Room(**r))

        db.session.commit()

        # 2.6. Nạp Bảng trung gian Movie_Genre
        # (LƯU Ý: Không dùng Model **g được vì đây là db.Table)
        for mg in load_json("moviegenre.json"):
            # Bỏ qua key "id" trong file json vì db.Table không cần id
            stmt = movie_genre.insert().values(movie_id=mg['movie_id'], genre_id=mg['genre_id'])
            db.session.execute(stmt)

        # 2.7. Nạp Seats
        for s in load_json("seat.json"):
            db.session.add(Seat(**s))

        db.session.commit()

        # 2.8. Nạp Showtimes (Xử lý datetime)
        for st in load_json("showtime.json"):
            st['start_time'] = datetime.strptime(st['start_time'], "%Y-%m-%d %H:%M:%S")
            st['end_time'] = datetime.strptime(st['end_time'], "%Y-%m-%d %H:%M:%S")
            db.session.add(Showtime(**st))

        db.session.commit()

        # 2.9. Nạp ShowtimeSeats (Xử lý Enum)
        for ss in load_json("showtimeseat.json"):
            ss['status'] = SeatStatus(ss['status'])
            db.session.add(ShowtimeSeat(**ss))

        db.session.commit()

        # 2.10. Nạp Bookings (Xử lý Enum)
        for b in load_json("booking.json"):
            b['status'] = BookingStatus(b['status'])
            db.session.add(Booking(**b))

        db.session.commit()

        # 2.11. Nạp Tickets
        for t in load_json("ticket.json"):
            db.session.add(Ticket(**t))

        db.session.commit()

        print("ĐÃ SEED DỮ LIỆU THÀNH CÔNG!")
