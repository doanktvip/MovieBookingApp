from flask import Flask

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "nguyenvandoansieudeptrai"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:hod2t123@localhost/moviedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 3

db = SQLAlchemy(app)


