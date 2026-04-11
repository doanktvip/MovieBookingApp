import math
import re
import uuid
import unicodedata
from datetime import datetime, timedelta
from movieapp import app, dao, login_manager, utils, db
from flask import Flask, render_template, request, url_for, redirect, flash, session, abort, jsonify
from flask_login import login_user, current_user, logout_user
from movieapp.decorators import staff_required, login_user_required, anonymous_required, user_required
from movieapp.models import User, TranslationType, Ticket, ShowtimeSeat, SeatStatus, BookingStatus, Booking
from momo_payment import create_momo_payment


@app.before_request
def assign_session_id():
    if 'user_session_id' not in session:
        session['user_session_id'] = str(uuid.uuid4())
        session.modified = True


# Trang chủ
@app.route('/')
def index():
    movies = dao.load_movies()
    genres = dao.load_genres()
    tien_ich = dao.load_tien_ich()
    return render_template('index.html', movies=movies, genres=genres, tien_ich=tien_ich)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    next_url = request.form.get('next')

    user = dao.auth_user(username=username, password=password)

    if user:
        login_user(user)
        flash("Đăng nhập thành công", "success")

        return redirect(next_url or url_for('index'))
    else:
        flash("Username hoặc password không đúng", "danger")

        return redirect(request.referrer or url_for('index', error='login'))


@login_manager.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash("Mật khẩu xác nhận không khớp!", "danger")
        return redirect(url_for('index', error='register'))

    if User.query.filter_by(username=username).first() is not None:
        flash("Tài khoản đã tồn tại!", "danger")
        return redirect(url_for('index', error='register'))

    try:
        dao.add_user(username=username, email=email, password=password)
        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for('index', success='register'))
    except Exception as e:
        print(str(e))
        flash("Đăng ký thất bại. Tên đăng nhập hoặc Email đã tồn tại!", "danger")
        return redirect(url_for('index', error='register'))


@app.route("/movies")
def movie():
    kw = request.args.get('keyword', '')
    genre_id = request.args.get('genre', '')
    page = request.args.get('page', 1, type=int)

    movies = dao.load_movies(genre_id=genre_id, kw=kw, page=page)
    genres = dao.load_genres()

    total_movies = dao.count_movies(genre_id=genre_id, kw=kw)
    total_pages = math.ceil(total_movies / app.config.get('PAGE_SIZE'))
    page_range = dao.get_page_range(current_page=page, total_pages=total_pages)
    return render_template('movie.html', movies=movies, genres=genres, pages=total_pages, page=page, current_kw=kw,
                           current_genre=genre_id, page_range=page_range)


# Trang rạp phim
@app.route("/cinemas")
def cinema():
    keyword = request.args.get('keyword_cinema')
    page = request.args.get("page", default=1, type=int)
    province_id = request.args.get('province_id')
    provinces = dao.load_provinces()
    cinemas, total = dao.load_cinema(keyword=keyword, page=page, province_id=province_id)
    if total == 0:
        pages = 1
    else:
        pages = math.ceil(total / app.config['PAGE_SIZE'])
    page_range = dao.get_page_range(current_page=page, total_pages=pages)
    sorted_dates = [datetime.now() + timedelta(days=i) for i in range(7)]
    # Lấy ngày hiện tại trên URL (nếu không có thì lấy ngày hôm nay làm mặc định)
    current_date = request.args.get('date', sorted_dates[0].strftime('%Y-%m-%d'))
    movies = dao.load_movies()
    movie_showtimes = {}
    for c in cinemas:
        movie_showtimes[c.id] = {}
        for d in sorted_dates:
            date_str = d.strftime('%Y-%m-%d')
            movie_showtimes[c.id][date_str] = dao.get_showtimes_by_movie_and_date(c.id, date_str)

    return render_template('cinema.html', cinemas=cinemas, page=page, pages=pages, provinces=provinces,
                           sorted_dates=sorted_dates, current_date=current_date, get_vn_weekday=get_vn_weekday,
                           movies=movies, movie_showtimes=movie_showtimes, page_range=page_range)


def get_vn_weekday(d):
    weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    return weekdays[d.weekday()]


@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    movie_info = dao.get_movie_by_id(movie_id)
    sorted_dates = [datetime.now() + timedelta(days=i) for i in range(7)]
    movie_format = dao.get_movie_format_all()

    default_date = sorted_dates[0].strftime('%Y-%m-%d')
    date_filter = request.args.get('date', default_date)
    format_filter = request.args.get('format', '')
    lang_filter = request.args.get('language', '')
    page = request.args.get('page', 1, type=int)

    cinema_showtimes, total_pages = dao.get_showtimes_grouped_by_cinema(movie_id, date_filter, format_filter,
                                                                        lang_filter, page=page)
    page_range = dao.get_page_range(page, total_pages)
    return render_template('movie-detail.html', movie=movie_info, sorted_dates=sorted_dates,
                           get_vn_weekday=get_vn_weekday, movie_format=movie_format, TranslationType=TranslationType,
                           cinema_showtimes=cinema_showtimes, total_pages=total_pages, page=page, page_range=page_range,
                           current_date=date_filter, current_format=format_filter, current_lang=lang_filter)


def slugify(text):
    # Loại bỏ dấu tiếng Việt và dấu câu
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Xóa ký tự đặc biệt và viết thường
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    # Gắn kết các từ bằng dấu gạch ngang
    text = re.sub(r'[-\s]+', '-', text)
    return text


@app.context_processor
def common_attribute():
    return {
        "slugify": slugify
    }


@app.route('/booking/showtime-<int:showtime_id>-<string:cinema_slug>-room-<int:room_id>')
@user_required
def booking(showtime_id, cinema_slug, room_id):
    showtime = dao.get_showtime_by_id(showtime_id)
    if not showtime or showtime.room_id != room_id:
        abort(404)

    dao.release_expired_seats(showtime_id)

    current_sid = session.get('user_session_id')
    time_remaining = 0
    booking_session = session.get('booking', {})

    if current_sid:
        expire_time = dao.get_reservation_expiry_time(current_sid, showtime_id)

        if expire_time:
            now = datetime.utcnow()
            time_remaining = math.ceil((expire_time - now).total_seconds())
        else:
            dao.clear_db_booking_by_session(current_sid)
            session.pop('booking', None)
            session.modified = True
            booking_session = {}

    showtime_seats = dao.get_seats_by_showtime(showtime_id)
    seat_map = {}
    for st_seat in showtime_seats:
        row = st_seat.seat.row
        col = st_seat.seat.col
        if row not in seat_map:
            seat_map[row] = {}
        seat_map[row][col] = st_seat

    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = list(range(1, 9))
    seat_type_vip = dao.get_seat_type(2)

    return render_template('booking.html', showtime=showtime, movie=showtime.movie, cinema=showtime.room.cinema,
                           room=showtime.room, seat_map=seat_map, rows=rows, cols=cols, seat_type_vip=seat_type_vip,
                           time_remaining=time_remaining, booking_session=booking_session)


@app.route('/api/booking', methods=['POST'])
def api_booking():
    data = request.json
    selected_seats = data.get('seats', [])
    current_session_id = session.get('user_session_id')

    booking_dict, expire_time = dao.process_seat_reservations(current_session_id, selected_seats)

    now = datetime.utcnow()

    if expire_time is None or expire_time <= now:
        session['booking'] = {}
        time_remaining = 0
        is_expired = True if selected_seats else False
    else:
        session['booking'] = booking_dict
        time_remaining = math.ceil((expire_time - now).total_seconds())
        is_expired = False

    session.modified = True

    response_data = utils.stats_seats(session['booking'])
    response_data['time_remaining'] = time_remaining
    response_data['expired'] = is_expired
    return jsonify(response_data)


@app.route('/api/clear-booking-session', methods=['POST'])
def clear_booking_session():
    current_sid = session.get('user_session_id')
    if current_sid:
        dao.clear_db_booking_by_session(current_sid)

    session.pop('booking', None)
    session.modified = True

    return jsonify({"status": "cleared"})


# Thanh toán
@app.route("/checkout", methods=['GET', 'POST'])
@login_user_required
def pay():
    showtime_id = request.form.get('showtime_id')
    showtime = dao.get_showtime_by_id(showtime_id)

    if not showtime:
        abort(404)

    # Lấy thông tin giỏ hàng và thời gian giữ ghế từ Session
    booking_session = session.get('booking')
    current_sid = session.get('user_session_id')
    expire_time = dao.get_reservation_expiry_time(current_sid, showtime_id)
    now = datetime.utcnow()

    # 1. BẢO MẬT: Kiểm tra xem user có lách luật vào thẳng link không, hoặc hết giờ giữ ghế
    if not booking_session or not expire_time or now >= expire_time:
        flash("Phiên giữ ghế đã hết hạn hoặc bạn chưa chọn ghế!", "danger")
        cinema_slug = slugify(showtime.room.cinema.name)
        return redirect(url_for('booking', showtime_id=showtime.id, cinema_slug=cinema_slug, room_id=showtime.room_id))

    # Tính toán thời gian còn lại & Tổng tiền (dùng hàm utils bạn đã import sẵn)
    time_remaining = int((expire_time - now).total_seconds())
    stats = utils.stats_seats(booking_session)

    # 3. Đẩy sang trang thanh toán
    return render_template('checkout.html', showtime=showtime, movie=showtime.movie, cinema=showtime.room.cinema,
                           room=showtime.room, booking_session=booking_session, stats=stats,
                           time_remaining=time_remaining)


@app.route("/process_payment", methods=['POST', 'GET'])
def process_payment():
    showtime_id = request.form.get('showtime_id')
    payment_method = request.form.get('payment_method')
    booking_session = session.get('booking')
    current_sid = session.get('user_session_id')

    if not booking_session:
        abort(404)
    # Tính thời gian hết hạn phụ thuộc giữ ghế
    expire_time = dao.get_reservation_expiry_time(current_sid, showtime_id)
    now = datetime.utcnow()
    if expire_time and expire_time > now:
        time_remaining_seconds = int((expire_time - now).total_seconds())
        expire_minutes = math.ceil(time_remaining_seconds / 60)
    else:
        flash("Phiên giữ ghế đã hết hạn, vui lòng chọn lại!", "danger")
        return redirect(url_for('index'))
    stats = utils.stats_seats(booking_session)
    total_amount = stats['total_amount']

    # Tạo booking pending trc khi qua Momo
    user_id = current_user.id if current_user.is_authenticated else None
    try:
        booking_id = dao.create_pending_booking(user_id, showtime_id, total_amount, booking_session)
    except Exception as e:
        flash("Lỗi hệ thống khi tạo đơn hàng, vui lòng thử lại!", "danger")
        return redirect(url_for('checkout'))

    # Tạo mã đơn hàng duy nhất (Ví dụ: DDN-12345678)
    order_id = f"DDN-{uuid.uuid4().hex[:8].upper()}"
    session['customer_info'] = {
        'order_id': order_id,
        "booking_id": booking_id,
        'name': current_user.username,
        'email': current_user.email,
        'showtime_id': showtime_id,
        'payment_method': payment_method,
        'total_amount': total_amount
    }
    session.modified = True

    if payment_method == 'momo':
        order_info = f"Thanh toan ve xem phim"

        # Đường dẫn MoMo sẽ đá khách về sau khi quét QR xong (Ta sẽ tạo ở Bước 3)
        redirect_url = url_for('momo_return', _external=True)
        ipn_url = url_for('momo_return', _external=True)  # (Tạm dùng chung cho môi trường test)

        # Gọi API MoMo
        momo_response = create_momo_payment(order_id, total_amount, order_info, redirect_url, ipn_url, expire_minutes)

        # Nếu MoMo trả về link thanh toán thành công
        if 'payUrl' in momo_response:
            return redirect(momo_response['payUrl'])  # CHUYỂN HƯỚNG KHÁCH SANG MOMO
        else:
            flash(f"Lỗi khởi tạo MoMo: {momo_response.get('message')}", "danger")
            return redirect(url_for('checkout'))

    return "Chức năng thanh toán khác đang cập nhật"


@app.route('/momo_return')
def momo_return():
    # 1. MoMo trả về một đống dữ liệu qua thanh URL (GET request)
    result_code = request.args.get('resultCode')
    order_id = request.args.get('orderId')
    message = request.args.get('message')

    customer_info = session.get('customer_info')
    current_sid = session.get('user_session_id')

    if not customer_info:
        flash("Lỗi: Phiên giao dịch đã hết hạn hoặc không tồn tại!", "danger")
        return redirect(url_for('index'))

    booking_id = customer_info.get('booking_id')

    # 2. Xử lý kết quả
    if result_code == "0":  # Code '0' của MoMo nghĩa là thanh toán THÀNH CÔNG
        try:
            dao.update_status_booking(booking_id, BookingStatus.PAID, current_sid)

            # Dọn dẹp session
            session.pop('booking', None)
            session.pop('customer_info', None)
            dao.clear_db_booking_by_session(current_sid)

            flash(f"Thanh toán MoMo thành công! Mã đơn hàng: {booking_id}", "success")
            return redirect(url_for('index'))

        except Exception as e:
            flash("Đã thanh toán nhưng lỗi lưu vé, vui lòng liên hệ CSKH!", "danger")
            return redirect(url_for('index'))

    else:
        # Code khác '0' nghĩa là thất bại (Khách hủy giao dịch, không đủ tiền...)
        dao.update_status_booking(booking_id, BookingStatus.PENDING, current_sid)

        flash(f"Giao dịch thất bại hoặc đã bị hủy. Lỗi: {message}", "danger")
        return redirect(url_for('index'))


@app.route('/userinfo', methods=['GET'])
@login_user_required
def userinfo():
    return render_template("userinfo.html")


@app.route('/edit-profile', methods=['POST'])
@login_user_required
def edit_profile():
    email = request.form.get('email')
    avatar_file = request.files.get('avatar')

    success, message = dao.update_user_profile(user_id=current_user.id, email=email, avatar_file=avatar_file)

    flash(message, "success" if success else "danger")
    return redirect(url_for('userinfo'))


@app.route('/change-password', methods=['POST'])
@login_user_required
def change_password_route():
    old_pw = request.form.get('old_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')

    # Kiểm tra khớp mật khẩu mới ngay tại server
    if new_pw != confirm_pw:
        flash("Xác nhận mật khẩu mới không khớp!", "danger")
        return redirect(url_for('userinfo'))

    success, message = dao.change_password(current_user.id, old_pw, new_pw)

    flash(message, "success" if success else "danger")
    return redirect(url_for('userinfo'))


# Trang quản lý đặt vé(nhân viên)
@app.route('/check_in', methods=['POST', 'GET'])
@login_user_required
@staff_required
def check_in():
    # Bảo mật user
    if current_user.role.name not in ['STAFF', 'ADMIN']:
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect(url_for('index'))
    bookings = dao.load_bookings_for_checkin()
    if request.method == 'POST':
        booking = request.form.get('submit_checkin')
        if booking:
            b = Booking.query.get(booking)
            if b:
                for ticket in b.tickets:
                    ticket.is_checked_in = True
                try:
                    db.session.commit()
                    flash("Cập nhật thành công", 'success')
                    return redirect("/check_in")
                except:
                    db.session.rollback()
                    flash("Hệ thống bị lỗi!", 'danger')
                    return redirect("/check_in")
    return render_template("staff_check_in.html", bookings=bookings)


@app.route('/tickets')
@login_user_required
def my_tickets():
    page = request.args.get('page', 1, type=int)

    user_bookings = dao.get_bookings_by_user(user_id=current_user.id, page=page)

    total_bookings = dao.count_bookings_by_user(current_user.id)
    page_size = app.config.get('PAGE_SIZE', 5)
    total_pages = math.ceil(total_bookings / page_size)

    page_range = dao.get_page_range(current_page=page, total_pages=total_pages)

    return render_template('ticket.html', bookings=user_bookings, pages=total_pages, page=page, page_range=page_range)


@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_user_required
def cancel_ticket(booking_id):
    success = dao.cancel_booking(booking_id=booking_id, user_id=current_user.id)

    if success:
        flash("Đã hủy vé thành công!", "success")
    else:
        flash("Không thể hủy vé. Đơn hàng không tồn tại hoặc đã được xử lý!", "danger")

    return redirect(url_for('my_tickets'))


if __name__ == '__main__':
    app.run(debug=True)
