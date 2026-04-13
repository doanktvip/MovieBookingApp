from flask import Flask
from flask_babel import Babel
from flask_login import LoginManager
import cloudinary
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "nguyenvandoansieudeptrai"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:hod2t123@localhost/moviedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 4
app.config["HOLD_TIME_MINUTES"] = 1
app.config['BABEL_DEFAULT_LOCALE'] = 'vi'
cloudinary.config(cloud_name="dtqkyyzv7", api_key="368798656518318", api_secret="DJdPWyRK2AVwUKiap4QsjPD7nis")

babel = Babel(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from movieapp import admin
