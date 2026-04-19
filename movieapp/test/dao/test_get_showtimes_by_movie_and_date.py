from datetime import datetime
from movieapp.dao import get_showtimes_by_movie_and_date


# Kiểm tra lấy suất chiếu đúng rạp, đúng ngày
def test_get_showtimes_success(sample_showtimes_complex):
    data = sample_showtimes_complex

    cinema_id = data["cinemas"]["cgv_tan_phu"].id
    movie = data["movies"]["hot"]
    date_str = datetime.now().strftime("%Y-%m-%d")

    result = get_showtimes_by_movie_and_date(cinema_id=cinema_id, date_str=date_str)

    assert len(result) > 0
    assert movie in result

    assert result[movie][0].start_time.hour == 23


# Kiểm tra trường hợp ngày không có suất chiếu
def test_get_showtimes_wrong_date(sample_showtimes_complex):
    data = sample_showtimes_complex
    cinema_id = data["cinemas"]["cgv_tan_phu"].id

    result = get_showtimes_by_movie_and_date(cinema_id=cinema_id, date_str="2099-01-01")

    assert len(result) == 0


# Kiểm tra rạp khác không thấy suất chiếu của rạp này
def test_get_showtimes_different_cinema(sample_showtimes_complex):
    data = sample_showtimes_complex
    cinema_id_other = data["cinemas"]["cgv_crescent"].id
    date_str = datetime.now().strftime("%Y-%m-%d")

    result = get_showtimes_by_movie_and_date(cinema_id=cinema_id_other, date_str=date_str)

    assert len(result) == 0


# Kiểm tra với ID rạp không tồn tại
def test_get_showtimes_invalid_cinema(test_app):
    date_str = datetime.now().strftime("%Y-%m-%d")

    result = get_showtimes_by_movie_and_date(cinema_id=9999, date_str=date_str)

    assert result == {}
    assert len(result) == 0
