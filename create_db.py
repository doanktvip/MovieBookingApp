import hashlib
import json
import os
import random
import traceback
from datetime import datetime, timedelta

from movieapp import app, db
from movieapp.models import (
    User, Genre, Movie, movie_genre, Cinema, Room,
    Seat, Showtime, ShowtimeSeat, Booking, Ticket,
    UserRole, SeatStatus, BookingStatus, TranslationType,
    Province, MovieFormat, SeatType
)


def load_json(filename):
    """Hàm hỗ trợ đọc file JSON từ thư mục data"""
    filepath = os.path.join(os.path.dirname(__file__), 'movieapp', 'data', filename)
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    with app.app_context():
        # 1. Xóa sạch và khởi tạo lại cấu trúc Database
        db.drop_all()
        db.create_all()

        try:
            # --- PHẦN 1: NẠP DỮ LIỆU TĨNH TỪ JSON ---

            # Nạp Users (Băm mật khẩu và chuyển chuỗi thành Enum)
            users = []
            for u in load_json("user.json"):
                u['role'] = UserRole(u['role'].lower())
                u['password'] = hashlib.md5(u['password'].encode("utf-8")).hexdigest()
                users.append(User(**u))
            db.session.add_all(users)

            # Nạp dữ liệu cơ bản (Thể loại, Tỉnh thành, Định dạng, Rạp)
            db.session.add_all([Genre(**g) for g in load_json("genre.json")])
            db.session.add_all([Province(**p) for p in load_json("province.json")])
            db.session.add_all([MovieFormat(**mf) for mf in load_json("movie_format.json")])
            db.session.add_all([Cinema(**c) for c in load_json("cinema.json")])
            db.session.commit()

            # Nạp Phim (Xử lý chuỗi ngày tháng sang datetime object)
            movies_dict = {}
            movies_to_add = []
            for m in load_json("movie.json"):
                m['release_date'] = datetime.strptime(m['release_date'], "%Y-%m-%d")
                new_movie = Movie(**m)
                movies_to_add.append(new_movie)
                movies_dict[m['id']] = new_movie
            db.session.add_all(movies_to_add)
            db.session.commit()

            # Nạp Phòng chiếu
            rooms_data = load_json("room.json")
            if rooms_data:
                db.session.add_all([Room(**r) for r in rooms_data])
                db.session.commit()
            rooms_list = db.session.query(Room).all()

            # Nạp liên kết Phim - Thể loại (Dùng Bulk Insert cực nhanh)
            movie_genre_data = load_json("movie_genre.json")
            if movie_genre_data:
                db.session.execute(movie_genre.insert(), movie_genre_data)
            db.session.commit()

            # --- PHẦN 2: TỰ ĐỘNG SINH DỮ LIỆU ĐỘNG (GHẾ & LỊCH CHIẾU) ---

            # Tạo loại ghế
            st_normal = SeatType(name="Normal", surcharge=0)
            st_vip = SeatType(name="Vip", surcharge=20000)
            db.session.add_all([st_normal, st_vip])
            db.session.commit()

            # Tạo Sơ đồ ghế 8x8 cho TẤT CẢ các phòng
            seats = []
            for rm in rooms_list:
                for row_char in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                    # Hàng F, G, H là ghế VIP
                    type_id = st_vip.id if row_char in ["F", "G", "H"] else st_normal.id
                    for col_num in range(1, 9):
                        seats.append(Seat(room_id=rm.id, seat_number=f"{row_char}{col_num}",
                                          row=row_char, col=col_num, seat_type_id=type_id))
            db.session.add_all(seats)
            db.session.commit()

            # Tự động sinh Lịch chiếu thông minh (4 ca/ngày, không chồng chéo)
            movies_list = list(movies_dict.values())
            formats_list = db.session.query(MovieFormat).all()

            # Lịch chiếu bắt đầu từ 2 ngày trước để có dữ liệu "quá hạn"
            start_date = datetime.now().date() - timedelta(days=2)
            count_st = 0

            for rm in rooms_list:
                # Lấy sẵn danh sách ghế của phòng này để tạo ShowtimeSeat
                seats_in_room = db.session.query(Seat).filter(Seat.room_id == rm.id).all()

                # Trải dài lịch chiếu trong 8 ngày
                for day_offset in range(8):
                    curr_day = start_date + timedelta(days=day_offset)

                    # Random giờ mở cửa ca sáng (từ 08:00 đến 08:45)
                    morning_start_offset = random.randint(0, 45)
                    previous_end_time = datetime.combine(curr_day, datetime.min.time()).replace(hour=8,
                                                                                                minute=morning_start_offset)

                    # 4 ca chiếu mỗi ngày nối tiếp nhau
                    for _ in range(4):
                        # Chọn ngẫu nhiên phim và định dạng xoay vòng
                        mv = movies_list[count_st % len(movies_list)]
                        fmt = formats_list[count_st % len(formats_list)]

                        # Lấy thời lượng phim (mặc định 120p nếu thiếu data)
                        duration = mv.duration or 120

                        # Rạp nghỉ dọn dẹp ngẫu nhiên từ 15 - 30 phút
                        break_time = random.randint(15, 30)

                        # Tính giờ chiếu ca tiếp theo
                        start_t = previous_end_time + timedelta(minutes=break_time)
                        end_t = start_t + timedelta(minutes=duration)

                        # Cập nhật mốc thời gian cho vòng lặp sau
                        previous_end_time = end_t

                        # Tạo Suất chiếu
                        new_st = Showtime(
                            movie_id=mv.id,
                            room_id=rm.id,
                            format_id=fmt.id,
                            base_price=75000.0 + (5000 * (count_st % 4)),
                            translation=TranslationType.SUBTITLE if count_st % 2 == 0 else TranslationType.DUBBING,
                            start_time=start_t,
                            end_time=end_t
                        )
                        db.session.add(new_st)
                        db.session.flush()  # Lưu tạm để lấy ID suất chiếu
                        count_st += 1

                        # Tự động làm đầy sơ đồ ghế cho suất chiếu này
                        st_seats = [ShowtimeSeat(
                            showtime_id=new_st.id,
                            seat_id=s.id,
                            price=new_st.base_price + (s.seat_type.surcharge or 0),
                            status=SeatStatus.AVAILABLE
                        ) for s in seats_in_room]

                        db.session.add_all(st_seats)

                # Commit theo từng phòng để giải phóng bộ nhớ
                db.session.commit()

            # --- KẾT QUẢ ---
            total_st_seats = db.session.query(ShowtimeSeat).count()
            print(f"✅ THÀNH CÔNG! Đã hoàn tất nạp dữ liệu.")
            print(f"-> Đã sinh {count_st} suất chiếu.")
            print(f"-> Đã tạo tổng cộng {total_st_seats} ghế.")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ THẤT BẠI. Đã hoàn tác (rollback) toàn bộ dữ liệu.")
            print(f"Lý do lỗi: {e}\n")
            traceback.print_exc()
