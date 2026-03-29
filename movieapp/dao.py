import hashlib
import json
import math
from datetime import date, datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import contains_eager
from movieapp import db, app
from movieapp.models import Movie, Genre, User, Cinema, MovieFormat, Showtime, TranslationType, Room, Province, Seat, \
    ShowtimeSeat, SeatType, SeatStatus
import unicodedata


def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(username, email, password):
    hashed_password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(username=username, email=email, password=hashed_password)
    db.session.add(u)
    db.session.commit()


def load_movies(genre_id=None, kw=None, page=1):
    query = Movie.query
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if kw:
        query = query.filter(Movie.title.contains(kw))
    if page:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])
    return query.all()


def load_genres():
    return Genre.query.all()


def count_movies(genre_id=None, kw=None):
    query = Movie.query
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if kw:
        query = query.filter(Movie.title.contains(kw))
    return query.count()


def load_tien_ich():
    with open("data/tienich.json", encoding="utf-8") as f:
        tien_ich = json.load(f)
        return tien_ich


# Hàm chuẩn hóa tiếng Việt: Xóa dấu và chuyển chữ Đ/đ
def remove_accents(input_str):
    if not input_str:
        return ""
    # Chuẩn hóa unicode, tách dấu ra khỏi chữ cái
    s1 = unicodedata.normalize('NFD', input_str)
    # Xóa các ký tự dấu
    s2 = ''.join([c for c in s1 if unicodedata.category(c) != 'Mn'])
    # Xử lý riêng chữ đ/Đ của tiếng Việt và chuyển về chữ thường
    return s2.replace('đ', 'd').replace('Đ', 'D').lower()


def load_cinema(keyword=None, page=None, province_id=None):
    query = Cinema.query
    total = 0

    # Tìm kiếm theo khu vuc
    if province_id:
        query = query.filter(Cinema.province_id.__eq__(int(province_id)))

    all_cinemas = query.all()
    # tim kiem theo ten rap
    if keyword:
        keyword = remove_accents(keyword).strip()
        result = []
        for c in all_cinemas:
            name_clean = remove_accents(c.name)
            address_clean = remove_accents(c.address)
            if keyword in name_clean or keyword in address_clean:
                result.append(c)

        # Phân trang
        total = len(result)
        if page:
            start = (int(page) - 1) * app.config["PAGE_SIZE"]
            end = start + app.config["PAGE_SIZE"]
            result = result[start:end]
        return result, total
    else:
        total = query.count()
        if page:
            start = (int(page) - 1) * app.config["PAGE_SIZE"]
            end = start + app.config["PAGE_SIZE"]
            query = query.slice(start, end)
        return query.all(), total


def load_provinces():
    return Province.query.all()


def get_movie_by_id(movie_id):
    return Movie.query.get(movie_id)


def get_movie_format_all():
    return MovieFormat.query.all()


def get_showtimes_grouped_by_cinema(movie_id, date_str=None, format_str=None, lang_str=None, page=1):
    # Bắt đầu từ bảng Showtime (Suất chiếu), nối với Room (Phòng) và Cinema (Rạp)
    query = Showtime.query.join(Room).join(Cinema).filter(Showtime.movie_id == movie_id)
    # Lọc theo Ngày: Nếu có truyền ngày vào thì lọc theo ngày đó, nếu không thì lấy mặc định là ngày hôm nay.
    if date_str:
        query = query.filter(func.date(Showtime.start_time) == date_str)
    else:
        query = query.filter(func.date(Showtime.start_time) == date.today())
    # Lọc theo Định dạng (2D, 3D, IMAX...): Nếu người dùng chọn định dạng, nối thêm bảng MovieFormat để lọc.
    if format_str:
        query = query.join(MovieFormat).filter(MovieFormat.name == format_str)
    # Lọc theo Ngôn ngữ (Phụ đề, Lồng tiếng): So sánh với kiểu dữ liệu Enum TranslationType.
    if lang_str:
        query = query.filter(Showtime.translation == TranslationType(lang_str))
    # Lấy ID Rạp: Từ bộ lọc ở trên
    cinema_id_query = query.with_entities(Cinema.id).distinct()

    total_cinemas = cinema_id_query.count()
    total_pages = math.ceil(total_cinemas / app.config.get('PAGE_SIZE')) if total_cinemas > 0 else 0

    if page:
        start = (page - 1) * app.config.get('PAGE_SIZE')
        cinema_id_tuples = cinema_id_query.slice(start, start + app.config.get('PAGE_SIZE')).all()
    else:
        cinema_id_tuples = cinema_id_query.all()
    # Dữ liệu DB trả về dạng mảng tuple [(1,), (2,)]. Đoạn này rút gọn nó thành mảng số bình thường [1, 2].
    cinema_ids = [c[0] for c in cinema_id_tuples]
    # Nếu sau khi lọc mà không có rạp nào phù hợp, ta thoát hàm sớm và trả về kết quả rỗng luôn, không cần làm tiếp.
    if not cinema_ids:
        return {}, total_pages
    # Cập nhật lại câu truy vấn ban đầu: Báo cho hệ thống biết CHỈ lấy suất chiếu của các rạp nằm trong danh sách 'cinema_ids' (rạp của trang hiện tại).
    query = query.filter(Cinema.id.in_(cinema_ids))
    # TỐI ƯU CỰC KỲ QUAN TRỌNG: Dùng contains_eager để "gói" sẵn thông tin Room và Cinema vào chung với Showtime.
    query = query.options(contains_eager(Showtime.room).contains_eager(Room.cinema))
    # Sắp xếp: Gom các suất chiếu của cùng 1 rạp lại gần nhau (Cinema.id.asc()),
    query = query.order_by(Cinema.id.asc(), Showtime.start_time.asc())

    showtimes = query.all()
    # GOM NHÓM KẾT QUẢ ĐỂ TRẢ VỀ GIAO DIỆN
    cinema_dict = {}
    for st in showtimes:
        cinema = st.room.cinema
        if cinema not in cinema_dict:
            cinema_dict[cinema] = []
        cinema_dict[cinema].append(st)

    return cinema_dict, total_pages


def release_expired_seats(showtime_id=None):
    try:
        now = datetime.utcnow()
        query = ShowtimeSeat.query.filter(ShowtimeSeat.status == SeatStatus.RESERVED,
                                          ShowtimeSeat.hold_until < now)

        # Nếu có truyền showtime_id thì lọc chính xác, không thì dọn toàn bộ hệ thống
        if showtime_id:
            query = query.filter(ShowtimeSeat.showtime_id == showtime_id)

        expired_seats = query.all()

        for st_seat in expired_seats:
            st_seat.status = SeatStatus.AVAILABLE
            st_seat.hold_until = None
            st_seat.hold_session_id = None

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"LỖI DỌN GHẾ: {e}")


def get_showtime_by_id(showtime_id):
    return Showtime.query.get(showtime_id)


def get_seats_by_showtime(showtime_id):
    release_expired_seats(showtime_id)
    seats = ShowtimeSeat.query.join(Seat).filter(
        ShowtimeSeat.showtime_id == showtime_id
    ).order_by(Seat.row.asc(), Seat.col.asc()).all()

    return seats


def get_showtimes_by_movie_and_date(cinema_id, date_str=None):
    query = Showtime.query.join(Room).join(Cinema).filter(
        Cinema.id == cinema_id,
        func.date(Showtime.start_time) == date_str
    ).order_by(Showtime.start_time.asc()).all()

    # gom nhóm suất chiếu theo từng bộ phim
    movie_dict = {}
    for st in query:
        # lấy đối tượng phim của suất chiếu tương ứng
        movie = st.movie
        if not movie in movie_dict:
            movie_dict[movie] = []
        movie_dict[movie].append(st)
    return movie_dict


def get_seats_all():
    return Seat.query.all()


def get_seat_type(seat_type_id):
    return SeatType.query.get(seat_type_id)


def get_seat_by_id(seat_id):
    return Seat.query.get(seat_id)


def get_or_create_expire_time(session_id, selected_seat_ids):
    now = datetime.utcnow()

    # Nếu không chọn ghế nào -> Xóa sạch ngay
    if not selected_seat_ids:
        ShowtimeSeat.query.filter_by(hold_session_id=session_id).update({
            "status": SeatStatus.AVAILABLE,
            "hold_until": None,
            "hold_session_id": None
        })
        return None

    # Tìm ghế đang giữ
    user_held_seats = ShowtimeSeat.query.filter_by(hold_session_id=session_id).all()

    # KIỂM TRA HẾT HẠN: Nếu có ghế nhưng đã quá giờ -> XÓA SẠCH VÀ TRẢ VỀ NONE
    for st in user_held_seats:
        if st.hold_until and st.hold_until < now:
            # Xóa dấu vết của session này trong DB
            ShowtimeSeat.query.filter_by(hold_session_id=session_id).update({
                "status": SeatStatus.AVAILABLE,
                "hold_until": None,
                "hold_session_id": None
            })
            return None  # Trả về None để báo hiệu hết hạn thật sự

        if st.hold_until and st.hold_until > now:
            return st.hold_until

    # Nếu chọn ghế mới hoàn toàn
    hold_minutes = app.config.get("HOLD_TIME_MINUTES", 10)
    return now + timedelta(minutes=hold_minutes)


# ---  DỌN DẸP GHẾ BỎ TICK ---
def release_unselected_seats(session_id, selected_seat_ids):
    user_held_seats = ShowtimeSeat.query.filter_by(hold_session_id=session_id).all()

    for st_seat in user_held_seats:
        # Nếu ghế cũ không có mặt trong danh sách mới -> Nhả ra
        if str(st_seat.id) not in selected_seat_ids:
            st_seat.status = SeatStatus.AVAILABLE
            st_seat.hold_until = None
            st_seat.hold_session_id = None


# ---  KHÓA GHẾ MỚI VÀ TÍNH TIỀN ---
def reserve_and_calculate_seats(session_id, selected_seats, expire_time):
    booking_dict = {}

    for seat_data in selected_seats:
        st_seat_id = str(seat_data.get('id'))
        st_seat = ShowtimeSeat.query.get(st_seat_id)

        if st_seat:
            if st_seat.status == SeatStatus.AVAILABLE or str(st_seat.hold_session_id) == str(session_id):
                # Khóa ghế trong Database
                st_seat.status = SeatStatus.RESERVED
                st_seat.hold_until = expire_time
                st_seat.hold_session_id = str(session_id)

                # --- BẮT ĐẦU TÍNH TOÁN GIÁ ---
                # 1. Lấy giá gốc (ưu tiên giá lẻ của ghế, nếu không lấy giá chung của suất chiếu)
                base_price = float(st_seat.price or (st_seat.showtime.base_price if st_seat.showtime else 0) or 0)

                # 2. Lấy phụ phí từ Model Seat (thông qua SeatType)
                current_surcharge = 0
                if st_seat.seat and st_seat.seat.seat_type:
                    current_surcharge = float(st_seat.seat.seat_type.surcharge or 0)

                # 3. Tính tổng giá cho ghế này
                booking_dict[st_seat_id] = {
                    "id": st_seat_id,
                    "name": seat_data.get('name'),
                    "price": base_price,
                    "surcharge": current_surcharge
                }

    return booking_dict


# --- HÀM QUẢN LÝ: LƯU DATABASE ---
def process_seat_reservations(session_id, selected_seats):
    selected_st_ids = [str(s.get('id')) for s in selected_seats]

    # 1. Tính thời gian (Hàm này giờ kiêm luôn việc dọn dẹp nếu selected_st_ids rỗng)
    expire_time = get_or_create_expire_time(session_id, selected_st_ids)

    # 2. Nhả những ghế cũ mà không nằm trong danh sách mới chọn
    # (Chỉ chạy nếu có expire_time, nếu không thì hàm trên đã dọn sạch rồi)
    if expire_time:
        release_unselected_seats(session_id, selected_st_ids)
        # 3. Khóa ghế mới
        booking_dict = reserve_and_calculate_seats(session_id, selected_seats, expire_time)
    else:
        booking_dict = {}

    db.session.commit()
    return booking_dict, expire_time


def check_active_reservations(session_id):
    if not session_id:
        return False
    now = datetime.utcnow()
    return ShowtimeSeat.query.filter(
        ShowtimeSeat.hold_session_id == str(session_id),
        ShowtimeSeat.status == SeatStatus.RESERVED,
        ShowtimeSeat.hold_until > now
    ).first() is not None


def clear_db_booking_by_session(session_id):
    if not session_id: return
    try:
        ShowtimeSeat.query.filter_by(hold_session_id=str(session_id)).update({
            "status": SeatStatus.AVAILABLE,
            "hold_until": None,
            "hold_session_id": None
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
