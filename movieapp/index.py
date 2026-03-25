import hashlib
import math
from datetime import datetime, timedelta
from movieapp import app, dao, login_manager
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_login import login_user, current_user, logout_user
from movieapp.models import User, TranslationType


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


import math
from flask import request, session, render_template


@app.route("/movies")
def movie():
    if 'keyword' in request.args or 'genre' in request.args:
        session['keyword'] = request.args.get('keyword', '')
        session['genre'] = request.args.get('genre', '')
        session['page'] = 1

    elif 'page' in request.args:
        session['page'] = request.args.get('page', 1, type=int)

    kw = session.get('keyword', '')
    genre_id = session.get('genre', '')
    page = session.get('page', 1)

    movies = dao.load_movies(genre_id=genre_id, kw=kw, page=page)
    genres = dao.load_genres()
    total_movies = dao.count_movies(genre_id=genre_id, kw=kw)
    total_pages = math.ceil(total_movies / app.config.get('PAGE_SIZE'))

    return render_template('movie.html', movies=movies, genres=genres, pages=total_pages, page=page)


# Trang rạp phim
@app.route("/cinemas")
def cinema():
    keyword = request.args.get('keyword_cinema')
    page = request.args.get("page", default=1, type=int)
    province_id = request.args.get('province_id')
    provinces = dao.load_provinces()
    cinemas,total= dao.load_cinema(keyword=keyword,page=page,province_id=province_id)
    if total == 0:
        pages = 1
    else:
        pages = math.ceil(total / app.config['PAGE_SIZE'])
    return render_template('cinema.html', cinemas=cinemas, page=page, pages=pages,provinces=provinces)


def get_vn_weekday(d):
    weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    return weekdays[d.weekday()]


@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    movie_info = dao.get_movie_by_id(movie_id)
    sorted_dates = [datetime.now() + timedelta(days=i) for i in range(7)]
    movie_format = dao.get_movie_format_all()

    # Các khóa lưu trong session cho phim hiện tại
    session_date_key = f'date_movie_{movie_id}'
    session_format_key = f'format_movie_{movie_id}'
    session_lang_key = f'lang_movie_{movie_id}'
    session_page_key = f'page_movie_{movie_id}'  # THÊM KHÓA PAGE

    # Nếu người dùng thay đổi bộ lọc (ngày, định dạng, ngôn ngữ)
    if any(k in request.args for k in ('date', 'format', 'language')):
        if 'date' in request.args:
            session[session_date_key] = request.args.get('date')
        if 'format' in request.args:
            session[session_format_key] = request.args.get('format')
        if 'language' in request.args:
            session[session_lang_key] = request.args.get('language')

        # Đổi bộ lọc thì tự động reset trang về 1
        session[session_page_key] = 1

    # Nếu người dùng chỉ bấm chuyển trang
    elif 'page' in request.args:
        session[session_page_key] = request.args.get('page', 1, type=int)

    # Rút dữ liệu từ session ra để đi lấy database
    date_filter = session.get(session_date_key, sorted_dates[0].strftime('%Y-%m-%d'))
    format_filter = session.get(session_format_key, '')
    lang_filter = session.get(session_lang_key, '')
    page = session.get(session_page_key, 1)  # Lấy page từ session, mặc định là 1

    cinema_showtimes, pagination = dao.get_showtimes_grouped_by_cinema(
        movie_id, date_filter, format_filter, lang_filter, page=page
    )

    return render_template('movie-detail.html', movie=movie_info, sorted_dates=sorted_dates,
                           get_vn_weekday=get_vn_weekday, movie_format=movie_format, TranslationType=TranslationType,
                           cinema_showtimes=cinema_showtimes, pagination=pagination, current_date=date_filter,
                           current_format=format_filter, current_lang=lang_filter)


if __name__ == '__main__':
    app.run(debug=True)
