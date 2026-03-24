import hashlib
import json
from movieapp import db, app
from movieapp.models import Movie, Genre, User, Cinema
import unicodedata

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


def load_movies(genre_id=None, kw=None, page=1):
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


def count_movies(genre_id=None, kw=None):
    query = Movie.query
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if kw:
        query = query.filter(Movie.title.contains(kw))
    return query.count()


def load_tien_ich():
    with open("data/tienich.json", encoding="utf-8") as f:
        tien_ich = json.load(f)
        return tien_ich

# Hàm chuẩn hóa tiếng Việt: Xóa dấu và chuyển chữ Đ/đ
def remove_accents(input_str):
    if not input_str:
        return ""
    # Chuẩn hóa unicode, tách dấu ra khỏi chữ cái
    s1 = unicodedata.normalize('NFD', input_str)
    # Xóa các ký tự dấu
    s2 = ''.join([c for c in s1 if unicodedata.category(c) != 'Mn'])
    # Xử lý riêng chữ đ/Đ của tiếng Việt và chuyển về chữ thường
    return s2.replace('đ', 'd').replace('Đ', 'D').lower()

def load_cinema(keyword=None):
    all_cinemas = Cinema.query.all()
    query = Cinema.query
    #tim kiem theo ten rap
    if keyword:
        keyword = remove_accents(keyword).strip()
        result=[]
        for c in all_cinemas:
            name_clean=remove_accents(c.name)
            address_clean=remove_accents(c.address)
            if keyword in name_clean or keyword in address_clean:
                result.append(c)
        return result

    return query.all()