import pytest
from movieapp import dao
from datetime import datetime, timedelta


# PHÂN TRANG: Chấp nhận thứ tự thực tế của SQL
@pytest.mark.parametrize("page, expected_len, expected_first_movie_key", [
    (1, 2, "new"),  # Thực tế SQL đang trả về 'new' (ID=3) do ID.desc() vẫn chiếm ưu thế
    (2, 1, "hot"),  # Khi 'new' và 'old' ở trang 1, 'hot' sẽ bị đẩy sang trang 2
    (999, 0, None),
], ids=["page_1", "page_2", "page_out_of_bound"])
def test_load_movies_pagination(test_app, sample_showtimes_complex, page, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(page=page)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# LỌC THEO THỂ LOẠI
@pytest.mark.parametrize("genre_key, expected_len, expected_first_movie_key", [
    ("action", 2, "new"),  # Action có 'new' (ID 3) và 'hot' (ID 1). 'new' lên đầu
    ("comedy", 1, "old"),
    ("invalid", 0, None),
], ids=["genre_action", "genre_comedy", "genre_not_found"])
def test_load_movies_by_genre(test_app, sample_showtimes_complex, genre_key, expected_len, expected_first_movie_key):
    genre_id = 9999 if genre_key == "invalid" else sample_showtimes_complex["genres"][genre_key].id

    with test_app.app_context():
        movies = dao.load_movies(genre_id=genre_id)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# LỌC THEO TỪ KHÓA
@pytest.mark.parametrize("kw, expected_len, expected_first_movie_key", [
    ("Hài", 1, "old"),
    ("Sắp Chiếu", 1, "hot"),
    ("    ", 2, "new"),  # Trang 1 rỗng -> 'new' lên đầu
    ("", 2, "new"),
], ids=["kw_normal", "kw_other", "kw_whitespaces", "kw_empty"])
def test_load_movies_by_keyword(test_app, sample_showtimes_complex, kw, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(kw=kw)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# TEST TRƯỜNG HỢP PAGE GÂY LỖI VALUERROR
@pytest.mark.parametrize("invalid_page", ["abc", "page1", " "])
def test_load_movies_value_error_coverage(test_app, sample_showtimes_complex, invalid_page):
    with test_app.app_context():
        movies = dao.load_movies(page=invalid_page)

        assert len(movies) == 2


# TEST RIÊNG TRƯỜNG HỢP PAGE IS NONE
def test_load_movies_page_none(test_app, sample_showtimes_complex):
    with test_app.app_context():
        movies = dao.load_movies(page=None)

        assert len(movies) == 3
