from movieapp.dao import get_showtimes_by_movie_and_date
from movieapp.test.test_base import sample_showtime_data,sample_movies,sample_rooms,sample_cinemas,test_session,test_app

# Đúng rạp, đúng ngày, đúng phim
def test_get_showtimes_success(sample_showtime_data):
    data = sample_showtime_data
    result = get_showtimes_by_movie_and_date(cinema_id=data['cinema_1_id'],date_str="2026-04-15")

    assert len(result) == 2
    assert data['movie_1'] in result
    assert data['movie_2'] in result

    #Phim 1 ở rạp 1 phải có 2 suất chiếu và đúng giờ bắt đầu
    assert len(result[data["movie_1"]]) == 2
    assert result[data["movie_1"]][0].start_time.hour==10
    assert result[data["movie_1"]][1].start_time.hour == 13

def test_get_showtimes_wrong_date(sample_showtime_data):
    data = sample_showtime_data
    result = get_showtimes_by_movie_and_date(cinema_id=data['cinema_1_id'], date_str="2026-04-01")
    assert len(result) == 0

def test_get_showtimes_different_cinema(sample_showtime_data):
    data = sample_showtime_data
    result = get_showtimes_by_movie_and_date(cinema_id=data['cinema_2_id'], date_str="2026-04-15")
    assert len(result) == 1
    assert data['movie_1'] in result
    assert result[data["movie_1"]][0].start_time.hour==20

def test_get_showtimes_wrong_cinema(sample_showtime_data):
    result = get_showtimes_by_movie_and_date(cinema_id=999, date_str="2026-04-15")

    assert result == {}
    assert len(result) == 0



