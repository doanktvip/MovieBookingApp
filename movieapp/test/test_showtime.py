import pytest
from datetime import date, timedelta
from movieapp import dao
from movieapp.test.test_base import test_session, test_app, sample_full_chain, sample_users, sample_showtimes_complex, \
    sample_movies_data, sample_cinemas, sample_basic_setup


@pytest.mark.parametrize("date_offset, format_name, lang_name, page, expected_count", [
    (0, None, None, 1, 1),  # Test thành công: Lấy đúng suất chiếu đã tạo (mặc định là hôm nay)
    (1, None, None, 1, 0),  # Test lọc theo ngày: Ngày mai (không có suất chiếu)
    (0, "2D", None, 1, 1),  # Test lọc theo định dạng: Đúng định dạng '2D'
    (0, "3D", None, 1, 0),  # Test lọc theo định dạng: Sai định dạng '3D'
    (0, None, "SUBTITLE", 1, 1),  # Test lọc theo ngôn ngữ: Đúng 'SUBTITLE' (Vietsub)
    (0, None, "VOICE", 1, 0),  # Test lọc theo ngôn ngữ: Sai 'VOICE' (Lồng tiếng)
    (0, None, None, 2, 0),  # Test phân trang: Page 2 (vượt quá số lượng rạp hiện có)
], ids=["default_today_success", "tomorrow_no_showtime", "format_2d_match", "format_3d_mismatch", "lang_subtitle_match",
        "lang_voice_mismatch", "page_2_empty"])
def test_get_showtimes_logic(test_app, sample_showtimes_complex, date_offset, format_name, lang_name, page,
                             expected_count):
    with test_app.app_context():
        data = sample_showtimes_complex
        movie_id = data["movies"]["hot"].id
        filter_date = (date.today() + timedelta(days=date_offset)).isoformat()
        cinema_dict, total_pages = dao.get_showtimes_grouped_by_cinema(movie_id=movie_id, date_str=filter_date,
                                                                       format_str=format_name, lang_str=lang_name,
                                                                       page=page)

        assert len(cinema_dict) == expected_count

        if expected_count > 0:
            for cinema, showtimes in cinema_dict.items():
                assert len(showtimes) > 0
                assert showtimes[0].movie_id == movie_id
            assert total_pages >= 1
        else:
            assert len(cinema_dict) == 0


# Test riêng biệt logic phân trang khi có nhiều rạp.
def test_get_showtimes_pagination_logic(test_app, sample_showtimes_complex):
    with test_app.app_context():
        data = sample_showtimes_complex
        movie_id = data["movies"]["hot"].id

        cinema_dict, total_pages = dao.get_showtimes_grouped_by_cinema(movie_id=movie_id, page=1)
        assert total_pages == 1


def test_get_showtimes_no_pagination(test_app, sample_showtimes_complex):
    with test_app.app_context():
        data = sample_showtimes_complex
        movie_id = data["movies"]["hot"].id

        cinema_dict, total_pages = dao.get_showtimes_grouped_by_cinema(movie_id=movie_id, page=None)

        assert len(cinema_dict) > 0
        assert total_pages == 1
