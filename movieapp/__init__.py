from flask import Flask

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "nguyenvandoansieudeptrai"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/moviedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 3

db = SQLAlchemy(app)

# thêm cái này m sửa được thì sửa chatlgpt nó bảo thế
from movieapp import admin
