import hashlib
from movieapp import app, dao, login_manager
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import login_user, current_user, logout_user
from movieapp.models import User


#Trang chủ
@app.route('/')
def index():
    movies=dao.load_movies()
    genres=dao.load_genres()
    return render_template('index.html',movies=movies,genres=genres)

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
        return redirect(url_for('index'))
    except Exception as e:
        print(str(e))
        flash("Đăng ký thất bại. Tên đăng nhập hoặc Email đã tồn tại!", "danger")
        return redirect(url_for('index', error='register'))

if __name__ == '__main__':
    app.run(debug=True)
