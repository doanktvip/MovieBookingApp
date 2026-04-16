import pytest

from movieapp import dao
from movieapp.test.conftest import test_session, sample_movies_data, test_app, sample_basic_setup, sample_cinemas


# ==========================================
# HÀM count_movies
# ==========================================
# Test đếm toàn bộ phim khi không truyền tham số
def test_count_movies_all(test_app, sample_movies_data):
    with test_app.app_context():
        total = dao.count_movies()
        assert total == 3


# Test đếm phim theo Thể loại hợp lệ
@pytest.mark.parametrize("genre_key, expected_count", [
    ("action", 2),  # Có 2 phim hành động
    ("comedy", 1),  # Có 1 phim hài
], ids=["count_action", "count_comedy"])
def test_count_movies_by_valid_genre(test_app, sample_movies_data, genre_key, expected_count):
    genre_id = sample_movies_data["genres"][genre_key].id
    with test_app.app_context():
        count = dao.count_movies(genre_id=genre_id)
        assert count == expected_count


# Test đếm phim với Thể loại không tồn tại
def test_count_movies_by_invalid_genre(test_app, sample_movies_data):
    with test_app.app_context():
        assert dao.count_movies(genre_id=9999) == 0


# Test đếm phim theo từ khóa với các trường hợp định dạng khác nhau
@pytest.mark.parametrize("kw, expected_count", [
    ("Sắp Chiếu", 1),  # Khớp 1 phần tên
    ("PHIM", 3),  # Không phân biệt hoa thường (Tìm chữ HOA)
    ("hài", 1),  # Không phân biệt hoa thường (Tìm chữ thường)
    ("", 3),  # Chuỗi rỗng -> Trả về tất cả phim
    ("   ", 0),  # Chuỗi toàn khoảng trắng
    ("@#$%", 0),  # Ký tự đặc biệt
], ids=["match_partial", "upper_case", "lower_case", "empty_kw", "spaces", "no_match"])
def test_count_movies_by_kw(test_app, sample_movies_data, kw, expected_count):
    with test_app.app_context():
        assert dao.count_movies(kw=kw) == expected_count


# Test kết hợp cả Thể loại và Từ khóa
@pytest.mark.parametrize("genre_key, kw, expected_count", [
    ("action", "Sắp Chiếu", 1),  # Khớp cả Thể loại và Từ khóa
    ("comedy", "Hành Động", 0),  # Thể loại Hài nhưng tìm chữ Hành động -> 0
    ("action", "", 2),  # Khớp Thể loại, từ khóa rỗng -> lấy hết phim của thể loại đó
], ids=["match_both_genre_and_kw", "conflict_genre_and_kw", "genre_with_empty_kw"])
def test_count_movies_combined(test_app, sample_movies_data, genre_key, kw, expected_count):
    genre_id = sample_movies_data["genres"][genre_key].id
    with test_app.app_context():
        assert dao.count_movies(genre_id=genre_id, kw=kw) == expected_count


# ==========================================
# HÀM get_movie_by_id
# ==========================================
# Test lấy phim với ID hợp lệ (Số nguyên)
def test_get_movie_by_id_success(test_app, sample_movies_data):
    m1 = sample_movies_data["movies"]["hot"]
    with test_app.app_context():
        actual_movie = dao.get_movie_by_id(m1.id)
        assert actual_movie is not None
        assert actual_movie.id == m1.id
        assert actual_movie.name == m1.name


# Test lấy phim nhưng truyền ID dạng chuỗi (String) xem DAO có ép kiểu tự động không
def test_get_movie_by_id_string_cast(test_app, sample_movies_data):
    m1 = sample_movies_data["movies"]["hot"]
    with test_app.app_context():
        actual_movie = dao.get_movie_by_id(str(m1.id))
        assert actual_movie is not None
        assert actual_movie.id == m1.id


# Test các trường hợp ID không hợp lệ hoặc không tồn tại
@pytest.mark.parametrize("invalid_id", [
    9999,  # ID không tồn tại
    0,  # ID bằng 0
    -5,  # ID âm
], ids=["not_exist", "zero_id", "negative_id"])
def test_get_movie_by_id_not_found(test_app, sample_movies_data, invalid_id):
    with test_app.app_context():
        assert dao.get_movie_by_id(invalid_id) is None


# ==========================================
# HÀM get_movie_format_all
# ==========================================
# Test lấy định dạng phim khi Database CÓ dữ liệu
def test_get_movie_format_all_with_data(test_app, sample_basic_setup):
    with test_app.app_context():
        formats = dao.get_movie_format_all()

        assert len(formats) == 2
        format_names = [f.name for f in formats]
        assert "2D" in format_names
        assert "3D" in format_names
