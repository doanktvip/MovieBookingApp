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


def load_movies( genre_id=None, kw=None, page=1):
    query = Movie.query
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if kw:
        query = query.filter(Movie.title.contains(kw))
    if page:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])
    return query.all()


def load_genres():
    return Genre.query.all()


def load_movie_genres():
    return Genre.query.all()

def count_movies(genre_id=None, kw=None):
    query = Movie.query
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if kw:
        query = query.filter(Movie.title.contains(kw))
    return query.count()
  
def load_tien_ich():
    with open("data/tienich.json",encoding="utf-8") as f:
        tien_ich = json.load(f)
        return tien_ich
