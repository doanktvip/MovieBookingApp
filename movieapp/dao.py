import hashlib
import json
from datetime import date
from sqlalchemy import func
from movieapp import db, app
from movieapp.models import Movie, Genre, User, Cinema, MovieFormat, Showtime, TranslationType, Room,Province
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

def load_cinema(keyword=None,page=None,province_id=None):
    query = Cinema.query
    total=0

    #Tìm kiếm theo khu vuc
    if province_id:
        query = query.filter(Cinema.province_id.__eq__(int(province_id)))

    all_cinemas = query.all()
    #tim kiem theo ten rap
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
        return result,total
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
    # 1. Khởi tạo truy vấn gốc: Kết nối Suất chiếu -> Phòng -> Rạp và lọc theo ID phim
    base_query = Showtime.query.join(Room).join(Cinema).filter(Showtime.movie_id == movie_id)

    # 2. Lọc theo ngày: Nếu có ngày truyền vào thì lọc, ngược lại mặc định lấy ngày hôm nay
    if date_str:
        base_query = base_query.filter(func.date(Showtime.start_time) == date_str)
    else:
        base_query = base_query.filter(func.date(Showtime.start_time) == date.today())

    # 3. Lọc theo định dạng phim (ví dụ: 2D, IMAX)
    if format_str:
        base_query = base_query.join(MovieFormat).filter(MovieFormat.name == format_str)

    # 4. Lọc theo ngôn ngữ (ví dụ: Phụ đề, Lồng tiếng)
    if lang_str:
        base_query = base_query.filter(Showtime.translation == TranslationType(lang_str))

    # 5. Truy vấn lấy danh sách ID của các rạp (dùng distinct để loại bỏ ID trùng lặp)
    cinema_ids_query = base_query.with_entities(Cinema.id).distinct().order_by(Cinema.id.asc())

    # 6. Thực hiện phân trang trên danh sách ID rạp (dựa vào cấu hình PAGE_SIZE)
    paginated_cinemas = cinema_ids_query.paginate(page=page, per_page=app.config["PAGE_SIZE"], error_out=False)

    # 7. Trích xuất ID rạp từ kết quả phân trang (chuyển từ dạng tuple [(1,), (2,)] sang list [1, 2])
    cinema_ids = [item[0] for item in paginated_cinemas.items]

    # 8. Xử lý ngoại lệ: Nếu không có rạp nào thỏa mãn bộ lọc, trả về dữ liệu rỗng ngay lập tức
    if not cinema_ids:
        return {}, paginated_cinemas

    # 9. Lấy danh sách suất chiếu chi tiết, giới hạn CHỈ TRONG CÁC RẠP của trang hiện tại
    showtimes = base_query.filter(Cinema.id.in_(cinema_ids)).order_by(Cinema.id.asc(), Showtime.start_time.asc()).all()

    # 10. Gom nhóm các suất chiếu vào dictionary theo cấu trúc: {<Cinema>: [<Showtime 1>, <Showtime 2>]}
    cinema_dict = {}
    for st in showtimes:
        cinema = st.room.cinema  # Lấy thông tin rạp từ suất chiếu

        # Nếu rạp chưa có trong từ điển, tạo một danh sách trống cho nó
        if cinema not in cinema_dict:
            cinema_dict[cinema] = []

        # Thêm suất chiếu vào danh sách của rạp tương ứng
        cinema_dict[cinema].append(st)

    # 11. Trả về từ điển đã gom nhóm và đối tượng phân trang (để vẽ nút Next/Prev ở HTML)
    return cinema_dict, paginated_cinemas

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