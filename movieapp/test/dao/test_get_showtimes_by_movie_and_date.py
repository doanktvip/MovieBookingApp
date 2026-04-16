from datetime import datetime
from movieapp.dao import get_showtimes_by_movie_and_date
from movieapp.test.conftest import test_app, sample_showtimes_complex


# ==========================================
# KIỂM THỬ TRUY VẤN SUẤT CHIẾU (READ)
# ==========================================

def test_get_showtimes_success(sample_showtimes_complex):
    """Kiểm tra lấy suất chiếu đúng rạp, đúng ngày"""
    data = sample_showtimes_complex

    # Lấy thông tin từ fixture (Tầng 5 đã tạo suất chiếu lúc 10h sáng hôm nay)
    cinema_id = data["cinemas"]["cgv_tan_phu"].id
    movie = data["movies"]["hot"]
    # Định dạng ngày theo yyyy-mm-dd để khớp với hàm DAO
    date_str = datetime.now().strftime("%Y-%m-%d")

    result = get_showtimes_by_movie_and_date(cinema_id=cinema_id, date_str=date_str)

    # Kiểm tra kết quả
    assert len(result) > 0
    assert movie in result
    # Kiểm tra giờ bắt đầu (Fixture tầng 5 đặt là 10h sáng)
    assert result[movie][0].start_time.hour == 10


def test_get_showtimes_wrong_date(sample_showtimes_complex):
    """Kiểm tra trường hợp ngày không có suất chiếu"""
    data = sample_showtimes_complex
    cinema_id = data["cinemas"]["cgv_tan_phu"].id

    # Truy vấn một ngày rất xa trong tương lai
    result = get_showtimes_by_movie_and_date(cinema_id=cinema_id, date_str="2099-01-01")

    assert len(result) == 0


def test_get_showtimes_different_cinema(sample_showtimes_complex):
    """Kiểm tra rạp khác không thấy suất chiếu của rạp này"""
    data = sample_showtimes_complex
    # Rạp 2 (cgv_crescent) không được tạo suất chiếu trong fixture tầng 5
    cinema_id_other = data["cinemas"]["cgv_crescent"].id
    date_str = datetime.now().strftime("%Y-%m-%d")

    result = get_showtimes_by_movie_and_date(cinema_id=cinema_id_other, date_str=date_str)

    assert len(result) == 0


def test_get_showtimes_invalid_cinema(test_app):
    """Kiểm tra với ID rạp không tồn tại"""
    # Cần test_app để có context database
    date_str = datetime.now().strftime("%Y-%m-%d")

    result = get_showtimes_by_movie_and_date(cinema_id=9999, date_str=date_str)

    assert result == {}
    assert len(result) == 0
