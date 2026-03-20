from movieapp import db,app
from movieapp.models import Movie,Genre,MovieGenre

def load_movies():
    return Movie.query.all()

def load_genres():
    return Genre.query.all()

def load_movie_genres():
    return Genre.query.all()
