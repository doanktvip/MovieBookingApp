import json

from movieapp import app, db
from movieapp.models import Genre, Movie, MovieGenre

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        print("--- Đã xóa sạch các bảng cũ ---")
        db.create_all()
        print("Đã tạo các bảng thành công trong MySQL!")
        with open("movieapp/data/genre.json", encoding="utf-8") as f:
            genres = json.load(f)
            for g in genres:
                genre = Genre(**g)
                db.session.add(genre)
            db.session.commit()
        with open("movieapp/data/movie.json", encoding="utf-8") as f:
            movies = json.load(f)
            for m in movies:
                movie = Movie(**m)
                db.session.add(movie)
            db.session.commit()
        with open("movieapp/data/moviegenre.json", encoding="utf-8") as f:
            movie_genres = json.load(f)
            for g in movie_genres:
                movie_genre = MovieGenre(**g)
                db.session.add(movie_genre)
        db.session.commit()
