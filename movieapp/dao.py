import hashlib
import json
import math
import re
from datetime import date, datetime, timedelta

from flask import current_app
from sqlalchemy import func, update, case, collate, or_
from sqlalchemy.orm import contains_eager
from movieapp import db, app
from movieapp.models import Movie, Genre, User, Cinema, MovieFormat, Showtime, TranslationType, Room, Province, Seat, \
    ShowtimeSeat, SeatType, SeatStatus, Ticket, Booking, BookingStatus
import unicodedata
import cloudinary.uploader


def is_valid_username_custom(text):
    """
    Trả về True nếu username:
    - Chỉ chứa ký tự Latinh (a-z, A-Z), số (0-9) và dấu gạch dưới (_).
    - KHÔNG chứa khoảng trắng.
    - KHÔNG chứa tiếng Việt có dấu hoặc ký tự đặc biệt khác.
    """
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, text))


def is_valid_email_custom(email):
    """
    Trả về True nếu email:
    - Tuân thủ định dạng email chuẩn (ví dụ: abc@gmail.com).
    - Cho phép chữ cái không dấu, số, dấu chấm (.), gạch dưới (_), gạch ngang (-).
    - KHÔNG chứa khoảng trắng.
    - KHÔNG chứa tiếng Việt có dấu.
    """
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_password_custom(text):
    """
    Trả về True nếu mật khẩu:
    - Chỉ chứa ký tự Latinh (a-z, A-Z), số (0-9).
    - Cho phép các ký tự đặc biệt: !@#$%^&*()_+-=[]{}|;:,.<>?
    - KHÔNG chứa khoảng trắng.
    - KHÔNG chứa tiếng Việt có dấu.
    """
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]+$'
    return bool(re.match(pattern, text))


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
    #  Kiểm tra các ràng buộc định dạng
    if not all([username, password]):
        raise ValueError("Vui lòng nhập đầy đủ thông tin!")

    if not is_valid_username_custom(username):
        raise ValueError("Tên đăng nhập chỉ được chứa chữ cái không dấu, số và '_', không có khoảng trắng!")

    if not is_valid_password_custom(password):
        raise ValueError("Mật khẩu không được dùng tiếng Việt hoặc khoảng trắng!")

    if not (6 <= len(username) <= 50) or not (6 <= len(password) <= 50):
        raise ValueError("Tên đăng nhập và mật khẩu phải từ 6 đến 50 ký tự!")

    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    user = User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()

    if user:
        if not user.active:
            raise ValueError("Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên!")

    return user


def get_user_by_id(user_id):
    return db.session.get(User, user_id)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def add_user(username, email, password):
    #  Kiểm tra các ràng buộc định dạng
    if not all([username, email, password]):
        raise ValueError("Vui lòng nhập đầy đủ thông tin!")

    if not is_valid_username_custom(username):
        raise ValueError("Tên đăng nhập chỉ được chứa chữ cái không dấu, số và '_', không có khoảng trắng!")

    if not is_valid_email_custom(email):
        raise ValueError("Email không được dùng tiếng Việt hoặc khoảng trắng!")

    if not is_valid_password_custom(password):
        raise ValueError("Mật khẩu không được dùng tiếng Việt hoặc khoảng trắng!")

    if not (6 <= len(username) <= 50) or not (6 <= len(password) <= 50):
        raise ValueError("Tên đăng nhập và mật khẩu phải từ 6 đến 50 ký tự!")

    # Kiểm tra trùng lặp bằng hàm chuyên biệt
    if get_user_by_username(username):
        raise ValueError("Tên đăng nhập đã tồn tại!")

    if get_user_by_email(email):
        raise ValueError("Email đã được sử dụng!")

    #  Thực hiện lưu dữ liệu
    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    u = User(username=username, email=email, password=hashed_password)

    try:
        db.session.add(u)
        db.session.commit()
        return u
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi không xác định: {e}")
        raise ValueError("Đã xảy ra lỗi hệ thống khi lưu dữ liệu!")


def load_movies(genre_id=None, kw=None, page=1):
    now = datetime.now()

    query = db.session.query(Movie).outerjoin(Showtime)

    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))

    if kw:
        query = query.filter(collate(Movie.name, 'utf8mb4_general_ci').like(f"%{kw.strip()}%"))

    upcoming_time = func.min(
        case(
            (Showtime.start_time >= now, Showtime.start_time),
            else_=None
        )
    )

    query = query.group_by(Movie.id).order_by(Movie.id.desc(), upcoming_time.is_(None), upcoming_time.asc())

    if page is not None:
        try:
            page_num = int(page)
            if page_num < 1:
                page_num = 1
        except ValueError:
            page_num = 1
        start = (page_num - 1) * current_app.config.get('PAGE_SIZE')
        query = query.offset(start).limit(current_app.config.get('PAGE_SIZE'))

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


def load_cinema(keyword=None, page=None, province_id=None):
    query = Cinema.query

    if province_id:
        query = query.filter(Cinema.province_id == int(province_id))

    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(or_(Cinema.name.ilike(kw), Cinema.address.ilike(kw)))

    total = query.count()

    # Phân trang chung cho mọi trường hợp
    if page:
        page_size = current_app.config["PAGE_SIZE"]
        query = query.offset((int(page) - 1) * page_size).limit(page_size)

    return query.all(), total


def load_provinces():
    return Province.query.all()


def get_movie_by_id(movie_id):
    return db.session.get(Movie, movie_id)


def get_movie_format_all():
    return MovieFormat.query.all()


def get_showtimes_grouped_by_cinema(movie_id, date_str=None, format_str=None, lang_str=None, page=1):
    query = Showtime.query.join(Room).join(Cinema).filter(Showtime.movie_id == movie_id)

    if date_str:
        query = query.filter(func.date(Showtime.start_time) == date_str)
    else:
        query = query.filter(func.date(Showtime.start_time) == date.today())

    if format_str:
        query = query.join(MovieFormat).filter(MovieFormat.name == format_str)

    if lang_str:
        try:
            lang_enum = TranslationType[lang_str]
            query = query.filter(Showtime.translation == lang_enum)
        except KeyError:
            return {}, 0

    cinema_id_query = query.with_entities(Cinema.id).distinct()

    total_cinemas = cinema_id_query.count()
    total_pages = math.ceil(total_cinemas / current_app.config.get('PAGE_SIZE')) if total_cinemas > 0 else 0

    if page:
        start = (page - 1) * current_app.config.get('PAGE_SIZE')
        cinema_id_tuples = cinema_id_query.slice(start, start + current_app.config.get('PAGE_SIZE')).all()
    else:
        cinema_id_tuples = cinema_id_query.all()

    cinema_ids = [c[0] for c in cinema_id_tuples]
    if not cinema_ids:
        return {}, total_pages

    query = query.filter(Cinema.id.in_(cinema_ids))
    query = query.options(contains_eager(Showtime.room).contains_eager(Room.cinema))
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


# Giải phóng ghế hết hạn
def release_expired_seats(showtime_id=None):
    try:
        now = datetime.now()

        expired_seats_query = db.session.query(ShowtimeSeat.id).filter(
            ShowtimeSeat.status == SeatStatus.RESERVED,
            ShowtimeSeat.hold_until < now
        )

        if showtime_id:
            expired_seats_query = expired_seats_query.filter(ShowtimeSeat.showtime_id == showtime_id)

        expired_seat_ids = [s.id for s in expired_seats_query.all()]

        if not expired_seat_ids:
            return

        related_bookings = db.session.query(Booking).join(Ticket).filter(
            Ticket.showtime_seat_id.in_(expired_seat_ids),
            Booking.status == BookingStatus.PENDING
        ).all()

        for booking in related_bookings:
            booking.status = BookingStatus.FAILED
            for t in booking.tickets:
                if t.showtime_seat:
                    t.showtime_seat.status = SeatStatus.AVAILABLE
                    t.showtime_seat.hold_until = None
                    t.showtime_seat.hold_session_id = None

        db.session.query(ShowtimeSeat).filter(
            ShowtimeSeat.id.in_(expired_seat_ids),
            ShowtimeSeat.status != SeatStatus.AVAILABLE
        ).update({
            ShowtimeSeat.status: SeatStatus.AVAILABLE,
            ShowtimeSeat.hold_until: None,
            ShowtimeSeat.hold_session_id: None
        }, synchronize_session=False)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi hiệu năng/logic: {e}")
        raise e


def release_single_seat_db(seat_id, session_id):
    try:
        s = ShowtimeSeat.query.filter_by(
            id=seat_id,
            hold_session_id=str(session_id)
        ).first()
        if s:
            s.status = SeatStatus.AVAILABLE
            s.hold_until = None
            s.hold_session_id = None
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi release_single_seat: {e}")


def get_showtime_by_id(showtime_id):
    return db.session.get(Showtime, showtime_id)


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
    return db.session.get(SeatType, seat_type_id)


def get_seat_by_id(seat_id):
    return db.session.get(Seat, seat_id)


# Đặt ghế
def process_seat_reservations_secure(user_id, session_id, showtime_id, selected_seats):
    now = datetime.now()
    selected_st_seat_ids = [str(s.get('id')) for s in selected_seats]

    # Ràng buộc: Kiểm tra thời gian chiếu phim
    st = db.session.get(Showtime, showtime_id)
    if not st:
        return False, "Suất chiếu không tồn tại.", {}, None
    if now >= st.start_time:
        return False, "Phim đã bắt đầu chiếu, không thể đặt vé.", {}, None

    # Ràng buộc: Tối đa 8 ghế / 1 người / 1 suất chiếu
    prev_tickets = db.session.query(Ticket).join(Booking).filter(
        Booking.user_id == user_id,
        Booking.showtime_id == showtime_id,
        Booking.status.in_([BookingStatus.PAID, BookingStatus.PENDING])).count()

    if prev_tickets + len(selected_st_seat_ids) > 8:
        return False, f"Bạn đã có {prev_tickets} vé cho suất này. Chỉ được đặt tối đa 8 ghế.", {}, None

    # Ràng buộc: Khóa dòng (with_for_update) và kiểm tra ghế đã có người đặt chưa
    seats_to_lock = ShowtimeSeat.query.with_for_update().filter(
        ShowtimeSeat.id.in_(selected_st_seat_ids),
        ShowtimeSeat.showtime_id == showtime_id
    ).all()

    if len(seats_to_lock) != len(selected_st_seat_ids):
        return False, "Một số ghế không hợp lệ hoặc không thuộc suất chiếu này.", {}, None

    hold_minutes = app.config.get("HOLD_TIME_MINUTES", 10)
    expire_time = now + timedelta(minutes=hold_minutes)
    booking_dict = {}

    for s in seats_to_lock:
        is_taken_by_others = (s.status == SeatStatus.RESERVED and
                              str(s.hold_session_id) != str(session_id) and
                              s.hold_until and s.hold_until > now)

        if s.status == SeatStatus.BOOKED or is_taken_by_others:
            return False, f"Ghế {s.seat.seat_number} vừa có người khác nhanh tay chọn mất.", {}, None

        # Đánh dấu giữ ghế
        s.status = SeatStatus.RESERVED
        s.hold_until = expire_time
        s.hold_session_id = str(session_id)

        # Lấy tên ghế gửi từ frontend để map
        seat_name = next((item['name'] for item in selected_seats if str(item['id']) == str(s.id)), "")
        booking_dict[str(s.id)] = {
            "id": str(s.id),
            "name": seat_name,
            "price": float(s.price or 0)
        }

    # Giải phóng các ghế cũ mà user đã bỏ tick (nếu trước đó có chọn)
    user_held_seats = ShowtimeSeat.query.filter_by(hold_session_id=str(session_id)).all()
    for s in user_held_seats:
        if str(s.id) not in selected_st_seat_ids:
            s.status = SeatStatus.AVAILABLE
            s.hold_until = None
            s.hold_session_id = None

    db.session.commit()
    return True, "Giữ ghế thành công", booking_dict, expire_time


# Hàm dọn dẹp khẩn cấp
def clear_db_booking_by_session(session_id):
    if not session_id: return
    try:
        ShowtimeSeat.query.filter_by(
            hold_session_id=str(session_id),
            status=SeatStatus.RESERVED
        ).update({
            "status": SeatStatus.AVAILABLE,
            "hold_until": None,
            "hold_session_id": None
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi dọn dẹp session {session_id}: {e}")


# Hàm trả về thời gian giữ ghế còn lại
def get_reservation_expiry_time(session_id, showtime_id):
    if not session_id:
        return None

    now = datetime.now()

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
            st_seat = db.session.get(ShowtimeSeat, st_seat_id)
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
        booking = db.session.get(Booking, booking_id)
        if not booking:
            raise Exception("Không tìm thấy đơn hàng!")
        booking.status = status
        now = datetime.now()

        if status == BookingStatus.PAID:
            # Thanh toán thành công
            for ticket in booking.tickets:
                st_seat = ticket.showtime_seat
                if st_seat:
                    # Kiểm tra bảo mật: Ghế có còn thuộc về người này không?
                    if current_sid and str(st_seat.hold_session_id) != str(current_sid):
                        raise Exception(
                            f"Ghế {st_seat.seat.row}{st_seat.seat.col} đã hết thời gian giữ và bị người khác lấy!")
                    if st_seat.hold_until and st_seat.hold_until < now:
                        raise Exception(
                            "Giao dịch trễ! Thời gian giữ ghế đã hết hạn trước khi hệ thống ghi nhận thanh toán.")

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
    user = db.session.get(User, user_id)
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
    user = db.session.get(User, user_id)
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
        page_size = current_app.config.get('PAGE_SIZE')
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)

    return query.all()


def cancel_booking(booking_id, user_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return False, "Đơn hàng không tồn tại!"

    # Kiểm tra check-in
    is_already_checked_in = any(ticket.is_checked_in for ticket in booking.tickets)
    if is_already_checked_in:
        return False, "Không thể hủy vé đã được check-in!"

    # Kiểm tra ràng buộc 2 giờ
    now = datetime.now()
    if booking.showtime:
        limit_time = booking.showtime.start_time - timedelta(hours=2)
        if now > limit_time:
            return False, "Chỉ được hủy vé trước giờ chiếu ít nhất 2 tiếng!"

    # Thực hiện hủy
    try:
        if booking.status != BookingStatus.CANCELLED:
            booking.status = BookingStatus.CANCELLED
            for ticket in booking.tickets:
                if ticket.showtime_seat:
                    ticket.showtime_seat.status = SeatStatus.AVAILABLE
                    ticket.showtime_seat.hold_until = None
                    ticket.showtime_seat.hold_session_id = None
                db.session.delete(ticket)
            db.session.commit()
            return True, "Đã hủy vé thành công!"
    except Exception as e:
        db.session.rollback()
        return False, f"Lỗi hệ thống: {str(e)}"

    return False, "Đơn hàng đã được hủy trước đó."


# Ticket
def load_bookings_for_checkin(kw=None, page=1):
    query = Booking.query.filter(Booking.status == BookingStatus.PAID)
    query = query.join(User)

    if kw:
        query = query.filter(User.username.like('%' + kw + '%'))
    total_count = query.count()
    page_size = app.config.get('PAGE_SIZE')
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    query = query.join(Showtime).order_by(Showtime.start_time.asc())

    # 2. (Phân trang)
    if page:
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)
    return query.all(), total_pages


def confirm_booking_checkin(booking_id):
    try:
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return False, "Không tìm thấy đơn hàng"
        for ticket in booking.tickets:
            ticket.is_checked_in = True

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False, str(e)
