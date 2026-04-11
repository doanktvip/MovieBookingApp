import hashlib
import json
import math
from datetime import date, datetime, timedelta
from sqlalchemy import func, update, case, collate
from sqlalchemy.orm import contains_eager
from movieapp import db, app
from movieapp.models import Movie, Genre, User, Cinema, MovieFormat, Showtime, TranslationType, Room, Province, Seat, \
    ShowtimeSeat, SeatType, SeatStatus, Ticket, Booking, BookingStatus
import unicodedata
import cloudinary.uploader


def get_page_range(current_page, total_pages, max_visible=3):
    if total_pages <= 1:
        return range(1, total_pages + 1)

    # Tính toán khoảng cách
    half = max_visible // 2
    start_page = current_page - half
    end_page = current_page + half

    # Xử lý nếu tràn về bên trái
    if start_page < 1:
        end_page += (1 - start_page)
        start_page = 1

    # Xử lý nếu tràn về bên phải
    if end_page > total_pages:
        start_page -= (end_page - total_pages)
        end_page = total_pages

    # Đảm bảo start_page không bao giờ nhỏ hơn 1 sau khi lùi lại
    start_page = max(1, start_page)

    return range(start_page, end_page + 1)


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
    now = datetime.utcnow()

    query = db.session.query(Movie).outerjoin(Showtime)

    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))

    if kw:
        query = query.filter(collate(Movie.name, 'utf8mb4_general_ci').like(f"%{kw}%"))

    upcoming_time = func.min(
        case(
            (Showtime.start_time >= now, Showtime.start_time),
            else_=None
        )
    )

    query = query.group_by(Movie.id).order_by(upcoming_time.is_(None), upcoming_time.asc(), Movie.created_at.desc())

    if page:
        start = (page - 1) * app.config.get('PAGE_SIZE')
        query = query.offset(start).limit(app.config.get('PAGE_SIZE'))

    return query.all()


def load_genres():
    return Genre.query.all()


def count_movies(genre_id=None, kw=None):
    query = Movie.query
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if kw:
        query = query.filter(collate(Movie.name, 'utf8mb4_general_ci').like(f"%{kw}%"))
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


# Quản lý bộ đếm thời gian
def get_or_create_expire_time(session_id, selected_seat_ids):
    now = datetime.utcnow()

    if not selected_seat_ids:
        ShowtimeSeat.query.filter_by(hold_session_id=session_id).update({
            "status": SeatStatus.AVAILABLE,
            "hold_until": None,
            "hold_session_id": None
        })
        return None

    user_held_seats = ShowtimeSeat.query.filter_by(hold_session_id=session_id).all()

    for st in user_held_seats:
        if st.hold_until and st.hold_until < now:
            ShowtimeSeat.query.filter_by(hold_session_id=session_id).update({
                "status": SeatStatus.AVAILABLE,
                "hold_until": None,
                "hold_session_id": None
            })
            return None

        if st.hold_until and st.hold_until > now:
            return st.hold_until

    hold_minutes = app.config.get("HOLD_TIME_MINUTES", 10)
    return now + timedelta(minutes=hold_minutes)


# Xử lý thao tác "Bỏ tick"
def release_unselected_seats(session_id, selected_seat_ids):
    user_held_seats = ShowtimeSeat.query.filter_by(hold_session_id=session_id).all()

    for st_seat in user_held_seats:
        if str(st_seat.id) not in selected_seat_ids:
            st_seat.status = SeatStatus.AVAILABLE
            st_seat.hold_until = None
            st_seat.hold_session_id = None


# Khóa an toàn và Tính tiền
def reserve_and_calculate_seats(session_id, selected_seats, expire_time):
    booking_dict = {}

    for seat_data in selected_seats:
        st_seat_id = str(seat_data.get('id'))

        st_seat = ShowtimeSeat.query.with_for_update().get(st_seat_id)

        if st_seat:
            if st_seat.status == SeatStatus.AVAILABLE or str(st_seat.hold_session_id) == str(session_id):
                st_seat.status = SeatStatus.RESERVED
                st_seat.hold_until = expire_time
                st_seat.hold_session_id = str(session_id)
                final_price = float(st_seat.price or 0)

                booking_dict[st_seat_id] = {
                    "id": st_seat_id,
                    "name": seat_data.get('name'),
                    "price": final_price
                }
            else:
                pass

    return booking_dict


# Hàm điều phối tổng
def process_seat_reservations(session_id, selected_seats):
    selected_st_ids = [str(s.get('id')) for s in selected_seats]

    expire_time = get_or_create_expire_time(session_id, selected_st_ids)

    if expire_time:
        release_unselected_seats(session_id, selected_st_ids)
        booking_dict = reserve_and_calculate_seats(session_id, selected_seats, expire_time)
    else:
        booking_dict = {}

    db.session.commit()
    return booking_dict, expire_time


# Hàm dọn dẹp khẩn cấp
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


# Hàm phục hồi trạng thái
def get_reservation_expiry_time(session_id, showtime_id):
    if not session_id:
        return None

    now = datetime.utcnow()

    active_seat = ShowtimeSeat.query.filter(
        ShowtimeSeat.hold_session_id == str(session_id),
        ShowtimeSeat.status == SeatStatus.RESERVED,
        ShowtimeSeat.showtime_id == showtime_id
    ).first()

    if active_seat and active_seat.hold_until:
        if active_seat.hold_until > now:
            return active_seat.hold_until

    return None


# Tạo booking(Pending)
def create_pending_booking(user_id, showtime_id, total_amount, booking_session):
    try:
        st_seat_ids = list(booking_session.keys())
        if not st_seat_ids:
            raise Exception("Đơn hàng trống!")

        first_st_seat_id = st_seat_ids[0]
        # Tìm ghế đầu có trong Ticket của Booking nào không
        existing_ticket = Ticket.query.join(Booking).filter(
            Ticket.showtime_seat_id == first_st_seat_id,
            Booking.status == BookingStatus.PENDING
        ).first()

        # Nếu tìm thấy
        if existing_ticket:
            existing_booking = existing_ticket.booking
            # DS ghế cũ
            old_seat_ids = [str(t.showtime_seat_id) for t in existing_booking.tickets]
            # TH1: Khách giữ ghế thanh toán lại
            if set(old_seat_ids) == set(st_seat_ids):
                existing_booking.total_price = total_amount

                db.session.commit()
                return existing_booking.id
            # TH 2: Khách đã đổi ý (quay lại chọn thêm hoặc bỏ bớt ghế) -> XÓA CŨ
            else:
                db.session.delete(existing_booking)
                db.session.flush()

        # Nếu chưa có thì tạo Hóa đơn tổng mới(Trạng thái PENDING)
        new_booking = Booking(
            user_id=user_id,
            showtime_id=showtime_id,
            total_price=total_amount,
            payment_method='MoMo',
            status=BookingStatus.PENDING
        )
        db.session.add(new_booking)
        db.session.flush()  # Lấy ID của booking vừa tạo

        # Tạo Vé lẻ cho từng ghế (nhưng ghế vẫn giữ nguyên trạng thái RESERVED)
        for st_seat_id, seat_data in booking_session.items():
            st_seat = ShowtimeSeat.query.get(st_seat_id)
            if st_seat:
                new_ticket = Ticket(
                    booking_id=new_booking.id,
                    showtime_seat_id=st_seat.id,
                    final_price=seat_data['price'] + seat_data.get('surcharge', 0)
                )
                db.session.add(new_ticket)

        db.session.commit()
        return new_booking.id  # Trả về mã đơn hàng để truyền qua MoMo

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi tạo Booking PENDING: {e}")
        raise e


# Cập nhật trạng thái booking
def update_status_booking(booking_id, status, current_sid=None):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            raise Exception("Không tìm thấy đơn hàng!")
        booking.status = status

        if status == BookingStatus.PAID:
            # Thanh toán thành công
            for ticket in booking.tickets:
                st_seat = ticket.showtime_seat
                if st_seat:
                    # Kiểm tra bảo mật: Ghế có còn thuộc về người này không?
                    if current_sid and str(st_seat.hold_session_id) != str(current_sid):
                        raise Exception(
                            f"Ghế {st_seat.seat.row}{st_seat.seat.col} đã hết thời gian giữ và bị người khác lấy!")
                    st_seat.status = SeatStatus.BOOKED
                    st_seat.hold_until = None
                    st_seat.hold_session_id = None
        elif status == BookingStatus.PENDING:
            # Nếu hủy thanh toán

            for ticket in booking.tickets:
                st_seat = ticket.showtime_seat
                if st_seat and current_sid and str(st_seat.hold_session_id) == str(current_sid):
                    st_seat.status = SeatStatus.RESERVED

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi cập nhật Booking: {e}")
        raise e


def get_or_create_province(name):
    name = name.strip()
    if not name:
        return None

    province = Province.query.filter_by(name=name).first()

    if not province:
        try:
            province = Province(name=name)
            db.session.add(province)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    return province


def upload_image(image_file, folder_name="movieapp"):
    if not image_file:
        return None

    try:
        upload_result = cloudinary.uploader.upload(image_file, folder=folder_name)
        return upload_result.get('secure_url')
    except Exception as e:
        print(f"Lỗi upload Cloudinary: {e}")
        return None


def update_future_showtime_seats_price(seat_type_id, new_surcharge):
    try:
        stmt = update(ShowtimeSeat).where(
            # 1. Lọc theo loại ghế
            ShowtimeSeat.seat_id.in_(
                db.session.query(Seat.id).filter(Seat.seat_type_id == seat_type_id)
            )
        ).where(
            # 2. Lọc suất chiếu tương lai
            ShowtimeSeat.showtime_id.in_(
                db.session.query(Showtime.id).filter(Showtime.start_time > datetime.now())
            )
        ).values(
            price=db.session.query(Showtime.base_price).filter(
                Showtime.id == ShowtimeSeat.showtime_id
            ).scalar_subquery() + new_surcharge
        )

        db.session.execute(stmt)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"DAO Error - Lỗi cập nhật giá ghế hàng loạt: {e}")
        return False


# Chỉnh sửa thông tin user
def update_user_profile(user_id, email, avatar_file=None):
    user = User.query.get(user_id)
    if not user:
        return False, "Không tìm thấy người dùng!"

    email_check = User.query.filter(User.id != user_id, User.email == email).first()
    if email_check:
        return False, "Email này đã được sử dụng!"

    if avatar_file and avatar_file.filename != '':
        new_avatar_url = upload_image(avatar_file)
        if new_avatar_url:
            user.avatar = new_avatar_url
        else:
            return False, "Lỗi khi tải ảnh lên hệ thống!"

    user.email = email

    try:
        db.session.commit()
        return True, "Cập nhật thông tin thành công!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


# Đổi mật khẩu
def change_password(user_id, old_password, new_password):
    user = User.query.get(user_id)
    if not user:
        return False, "Người dùng không tồn tại!"
    hashed_old = str(hashlib.md5(old_password.strip().encode('utf-8')).hexdigest())

    if user.password != hashed_old:
        return False, "Mật khẩu cũ không chính xác!"

    user.password = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())

    try:
        db.session.commit()
        return True, "Đổi mật khẩu thành công!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def count_bookings_by_user(user_id):
    return Booking.query.filter_by(user_id=user_id).count()


def get_bookings_by_user(user_id, page=1):
    query = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc())
    if page:
        page_size = app.config.get('PAGE_SIZE')
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)

    return query.all()


def cancel_booking(booking_id, user_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

    if booking:
        is_already_checked_in = any(ticket.is_checked_in for ticket in booking.tickets)

        if is_already_checked_in:
            return False

        if booking.status != BookingStatus.CANCELLED:
            booking.status = BookingStatus.CANCELLED

            for ticket in booking.tickets:
                if ticket.showtime_seat:
                    ticket.showtime_seat.status = SeatStatus.AVAILABLE
                    ticket.showtime_seat.hold_until = None
                    ticket.showtime_seat.hold_session_id = None
                db.session.delete(ticket)

            db.session.commit()
            return True

    return False


# Ticket
def load_bookings_for_checkin():
    query = Booking.query.filter(Booking.status == BookingStatus.PAID)
    return query.join(Showtime).order_by(Showtime.start_time.asc()).all()


def confirm_booking_checkin(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Không tìm thấy đơn hàng"
        for ticket in booking.tickets:
            ticket.is_checked_in = True

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False, str(e)
