import hashlib
import json
import math
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import contains_eager
from movieapp import db, app
from movieapp.models import Movie, Genre, User, Cinema, MovieFormat, Showtime, TranslationType, Room, Province, Seat, ShowtimeSeat
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


def get_showtime_by_id(showtime_id):
    return Showtime.query.get(showtime_id)


def get_seats_by_showtime(showtime_id):
    """
    Hàm này lấy tất cả các ghế của một suất chiếu,
    kết nối với bảng Seat để lấy số ghế và hàng,
    sau đó sắp xếp gọn gàng theo thứ tự A->Z, 1->10.
    """
    seats = ShowtimeSeat.query.join(Seat).filter(
        ShowtimeSeat.showtime_id == showtime_id
    ).order_by(Seat.row.asc(), Seat.col.asc()).all()

    return seats
#Lấy danh sách các suất chiếu tương ứng theo từng phim trong ngày cụ thể
def get_showtimes_by_movie_and_date(cinema_id, date_str=None):
    query = Showtime.query.join(Room).join(Cinema).filter(
        Cinema.id == cinema_id,
        func.date(Showtime.start_time) == date_str
    ).order_by(Showtime.start_time.asc()).all()

    #gom nhóm suất chiếu theo từng bộ phim
    movie_dict={}
    for st in query:
        # lấy đối tượng phim của suất chiếu tương ứng
        movie = st.movie
        if not movie in movie_dict:
            movie_dict[movie] = []
        movie_dict[movie].append(st)
    return movie_dict


