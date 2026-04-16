import pytest
from movieapp.dao import load_cinema
from movieapp.test.test_base import sample_cinemas, test_app, test_session,sample_basic_setup


# TÌM KIẾM THEO TỪ KHÓA (KEYWORD)
@pytest.mark.parametrize("keyword, expected_count", [
    (None, 3),
    ("Tân Phú", 1),
    ("SaiTenRap", 0),
], ids=["no_keyword_get_all", "exact_cinema_name_match", "keyword_not_found"])
def test_load_cinema_by_keyword(test_app, sample_cinemas, keyword, expected_count):
    with test_app.app_context():
        actual_cinemas, total = load_cinema(keyword=keyword)
        assert len(actual_cinemas) == expected_count
        assert total == expected_count


# LỌC THEO KHU VỰC (PROVINCE)
@pytest.mark.parametrize("province_id, expected_count", [
    (1, 2),
    (999, 0),
], ids=["province_has_2_cinemas", "province_not_found"])
def test_load_cinema_by_province(test_app, sample_cinemas, province_id, expected_count):
    with test_app.app_context():
        actual_cinemas, total = load_cinema(province_id=province_id)
        assert len(actual_cinemas) == expected_count
        assert total == expected_count


# KẾT HỢP TỪ KHÓA & KHU VỰC
@pytest.mark.parametrize("keyword, province_id, expected_count", [
    ("CGV", 1, 2),
    ("Tân Phú", 2, 0),
], ids=["match_both_keyword_and_province", "match_keyword_but_wrong_province"])
def test_load_cinema_combined_filter(test_app, sample_cinemas, keyword, province_id, expected_count):
    with test_app.app_context():
        actual_cinemas, total = load_cinema(keyword=keyword, province_id=province_id)
        assert len(actual_cinemas) == expected_count


# PHÂN TRANG KHI KHÔNG CÓ TỪ KHÓA
@pytest.mark.parametrize("page, expected_count, expected_total", [
    (1, 2, 3),
    (3, 0, 3),
], ids=["page_1_returns_page_size_limit", "page_out_of_bounds_returns_empty"])
def test_load_cinema_pagination_no_keyword(test_app, sample_cinemas, page, expected_count, expected_total):
    with test_app.app_context():
        actual_cinemas, total = load_cinema(page=page)
        assert len(actual_cinemas) == expected_count
        assert total == expected_total


# PHÂN TRANG KHI CÓ TỪ KHÓA
@pytest.mark.parametrize("keyword, page, expected_count, expected_total", [
    ("CGV", 1, 2, 3),
    ("CGV", 2, 1, 3),
], ids=["page_1_with_keyword_filter", "page_2_with_keyword_filter_remaining"])
def test_load_cinema_pagination_with_keyword(test_app, sample_cinemas, keyword, page, expected_count, expected_total):
    with test_app.app_context():
        actual_cinemas, total = load_cinema(keyword=keyword, page=page)
        assert len(actual_cinemas) == expected_count
        assert total == expected_total
