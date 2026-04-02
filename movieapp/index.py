import math
import re
import uuid

import unicodedata
from datetime import datetime, timedelta
from movieapp import app, dao, login_manager, utils
from flask import Flask, render_template, request, url_for, redirect, flash, session, abort, jsonify
from flask_login import login_user, current_user, logout_user
from movieapp.models import User, TranslationType


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

    user = dao.auth_user(username=username, password=password)

    if user:
        login_user(user)
        flash("Đăng nhập thành công", "success")
        return redirect(url_for('index'))
    else:
        flash("Username hoặc password không đúng", "danger")
        return redirect(url_for('index', error='login'))


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
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text


@app.context_processor
def common_attribute():
    return {
        "slugify": slugify
    }


@app.route('/booking/showtime-<int:showtime_id>-<string:cinema_slug>-room-<int:room_id>')
def booking(showtime_id, cinema_slug, room_id):
    showtime = dao.get_showtime_by_id(showtime_id)
    if not showtime or showtime.room_id != room_id:
        abort(404)

    # Dọn rác của suất chiếu này
    dao.release_expired_seats(showtime_id)

    current_sid = session.get('user_session_id')
    time_remaining = 0
    booking_session = session.get('booking', {})

    if current_sid:
        # GỌI HÀM DAO ĐỂ LẤY THỜI GIAN (Thay vì query trực tiếp như trước)
        expire_time = dao.get_reservation_expiry_time(current_sid, showtime_id)

        if expire_time:
            # Vẫn còn hạn -> Tính ra số giây để truyền xuống giao diện
            now = datetime.utcnow()
            time_remaining = int((expire_time - now).total_seconds())
        else:
            # Hết hạn hoặc không có ghế -> Báo DAO dọn dẹp DB và clear Session
            dao.clear_db_booking_by_session(current_sid)
            session.pop('booking', None)
            session.modified = True
            booking_session = {}

    # Lấy map ghế từ DAO
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

    return render_template('booking.html',
                           showtime=showtime,
                           movie=showtime.movie,
                           cinema=showtime.room.cinema,
                           room=showtime.room,
                           seat_map=seat_map,
                           rows=rows,
                           cols=cols,
                           seat_type_vip=seat_type_vip,
                           time_remaining=time_remaining,
                           booking_session=booking_session)


@app.route('/api/booking', methods=['POST'])
def api_booking():
    data = request.json
    selected_seats = data.get('seats', [])
    current_session_id = session.get('user_session_id')

    booking_dict, expire_time = dao.process_seat_reservations(current_session_id, selected_seats)

    time_remaining = 0
    now = datetime.utcnow()

    if expire_time is None or expire_time <= now:
        session['booking'] = {}
        time_remaining = 0
        is_expired = True if selected_seats else False
    else:
        session['booking'] = booking_dict
        time_remaining = int((expire_time - now).total_seconds())
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


if __name__ == '__main__':
    app.run(debug=True)
