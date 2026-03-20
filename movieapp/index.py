from movieapp import app, dao
from flask import Flask, render_template, request, url_for
from flask_login import login_user, current_user, logout_user


#Trang chủ
@app.route('/')
def index():
    movies=dao.load_movies()
    genres=dao.load_genres()
    return render_template('index.html',movies=movies,genres=genres)


if __name__ == '__main__':
    app.run(debug=True)
