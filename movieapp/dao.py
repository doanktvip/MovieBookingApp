import hashlib
import json

from movieapp import db,app
from movieapp.models import Movie,Genre,MovieGenre,User

def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(username, email, password):
    hashed_password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(username=username, email=email, password=hashed_password)
    db.session.add(u)
    db.session.commit()


def load_movies(limit=None):
    query=Movie.query
    if limit:
        query = query.limit(limit)
    return query.all()

def load_genres():
    return Genre.query.all()

def load_movie_genres():
    return Genre.query.all()
def load_tien_ich():
    with open("data/tienich.json",encoding="utf-8") as f:
        tien_ich = json.load(f)
        return tien_ich