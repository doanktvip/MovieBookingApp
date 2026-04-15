import pytest
from movieapp import dao
from movieapp.test.test_base import test_session, test_app, sample_showtimes_complex, sample_movies_data, \
    sample_cinemas, sample_basic_setup


# LẤY TẤT CẢ VÀ PHÂN TRANG
@pytest.mark.parametrize("page, expected_len, expected_first_movie_key", [
    (1, 2, "hot"),  # Trang 1 lấy 2 phim, phim "hot" (có suất chiếu) xếp đầu
    (2, 1, "old"),  # Trang 2 lấy 1 phim còn lại
    (999, 0, None),  # Trang vượt quá giới hạn -> Trả về rỗng
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
    ("action", 2, "hot"),  # Thể loại hành động có 2 phim
    ("comedy", 1, "old"),  # Thể loại hài có 1 phim
    ("invalid", 0, None),  # Thể loại không tồn tại -> rỗng
], ids=["genre_action", "genre_comedy", "genre_not_found"])
def test_load_movies_by_genre(test_app, sample_showtimes_complex, genre_key, expected_len, expected_first_movie_key):
    genre_id = 9999 if genre_key == "invalid" else sample_showtimes_complex["genres"][genre_key].id

    with test_app.app_context():
        movies = dao.load_movies(genre_id=genre_id)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# TÌM KIẾM THEO TỪ KHÓA (KEYWORD)
@pytest.mark.parametrize("kw, expected_len, expected_first_movie_key", [
    ("Hài", 1, "old"),  # Từ khóa bình thường
    ("hài", 1, "old"),  # Chữ hoa/thường lộn xộn (Case insensitive)
    ("Sắp Chiếu", 1, "hot"),  # Từ khóa khác
    ("Không Tồn Tại", 0, None),  # Từ khóa không có trong DB
    ("   ", 2, "hot"),  # Toàn khoảng trắng -> lờ đi, load tất cả
    ("", 2, "hot"),  # Chuỗi rỗng -> load tất cả
], ids=["kw_normal", "kw_lowercase", "kw_other", "kw_not_found", "kw_whitespaces", "kw_empty"])
def test_load_movies_by_keyword(test_app, sample_showtimes_complex, kw, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(kw=kw)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id


# LỌC KẾT HỢP (GENRE + KEYWORD)
@pytest.mark.parametrize("kw, genre_key, expected_len, expected_first_movie_key", [
    ("Sắp Chiếu", "action", 1, "hot"),  # Khớp cả từ khóa và thể loại
    ("hài", "action", 0, None),  # Từ khóa "Hài" nhưng chọn thể loại "Hành động" -> rỗng
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
    (0, 2, "hot"),  # Trang 0 -> Tự động fallback về trang 1
    (-5, 2, "hot"),  # Trang âm -> Tự động fallback về trang 1
], ids=["page_zero", "page_negative"])
def test_load_movies_page_edge_cases(test_app, sample_showtimes_complex, page, expected_len, expected_first_movie_key):
    with test_app.app_context():
        movies = dao.load_movies(page=page)

        assert len(movies) == expected_len
        if expected_first_movie_key:
            expected_movie = sample_showtimes_complex["movies"][expected_first_movie_key]
            assert movies[0].id == expected_movie.id
