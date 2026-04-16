from movieapp.dao import load_genres
from movieapp.test.conftest import test_session, test_app, sample_movies_data, sample_cinemas, sample_basic_setup


# ==========================================
# KIỂM THỬ TẢI THỂ LOẠI (READ)
# ==========================================

def test_load_genres_success(sample_movies_data):
    # 1. Gọi hàm DAO
    result = load_genres()

    # 2. Kiểm tra số lượng (Trong sample_movies_data bạn tạo: Hành động, Hài hước)
    assert len(result) == 2

    # 3. Kiểm tra tên các thể loại có khớp không
    result_names = [g.name for g in result]
    assert "Hành động" in result_names
    assert "Hài hước" in result_names
    assert "Phiêu lưu" not in result_names  # Vì fixture không tạo loại này


def test_load_genres_empty(test_app):
    result = load_genres()
    assert len(result) == 0
