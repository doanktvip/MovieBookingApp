import pytest
from movieapp import dao
from movieapp.test.test_base import test_session, test_app, sample_showtimes_complex, sample_movies_data, \
    sample_cinemas, sample_basic_setup


# LẤY TẤT CẢ VÀ PHÂN TRANG
@pytest.mark.parametrize("page, expected_len, expected_first_movie_key", [
    (1, 2, "new"),  # Trang 1 lấy 2 phim, phim mới nhất "new" (id=3) xếp đầu
    (2, 1, "hot"),  # Trang 2 lấy 1 phim còn lại (phim "hot" id=1)
    (999, 0, None),  # Trang vượt quá giới hạn
], ids=["page_1", "page_2", "page_out_of_bound"])
def test_load_movies_pagination(test_app, sample_showtimes_complex, page, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(page=page)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# LỌC THEO THỂ LOẠI (GENRE)
@pytest.mark.parametrize("genre_key, expected_len, expected_first_movie_key", [
    ("action", 2, "new"),  # Thể loại hành động có 'new' và 'hot'. 'new' id=3 lớn nhất nên xếp đầu
    ("comedy", 1, "old"),  # Thể loại hài chỉ có 'old'
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


# LỌC THEO TỪ KHÓA (KEYWORD)
@pytest.mark.parametrize("kw, expected_len, expected_first_movie_key", [
    ("Hài", 1, "old"),
    ("hài", 1, "old"),
    ("Sắp Chiếu", 1, "hot"),
    ("Không Tồn Tại", 0, None),
    ("    ", 2, "new"),  # Khoảng trắng coi như load tất cả trang 1 -> 'new' lên đầu
    ("", 2, "new"),  # Rỗng coi như load tất cả trang 1 -> 'new' lên đầu
], ids=["kw_normal", "kw_lowercase", "kw_other", "kw_not_found", "kw_whitespaces", "kw_empty"])
def test_load_movies_by_keyword(test_app, sample_showtimes_complex, kw, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(kw=kw)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# KẾT HỢP NHIỀU BỘ LỌC
@pytest.mark.parametrize("kw, genre_key, expected_len, expected_first_movie_key", [
    ("Sắp Chiếu", "action", 1, "hot"),
    ("hài", "action", 0, None),
], ids=["combined_match", "combined_conflict"])
def test_load_movies_combined_filters(test_app, sample_showtimes_complex, kw, genre_key, expected_len,
                                      expected_first_movie_key):
    genre_id = sample_showtimes_complex["genres"][genre_key].id

    with test_app.app_context():
        movies = dao.load_movies(kw=kw, genre_id=genre_id)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# TRƯỜNG HỢP RANH GIỚI TRANG (EDGE CASES)
@pytest.mark.parametrize("page, expected_len, expected_first_movie_key", [
    (0, 2, "new"),  # Trang 0 fallback về 1 -> 'new' đầu
    (-5, 2, "new"),  # Trang âm fallback về 1 -> 'new' đầu
], ids=["page_zero", "page_negative"])
def test_load_movies_page_edge_cases(test_app, sample_showtimes_complex, page, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(page=page)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id
