from movieapp import app
from flask import Flask, render_template, request, url_for
from flask_login import login_user, current_user, logout_user


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
