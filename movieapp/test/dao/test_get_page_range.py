import pytest
from movieapp import dao


# TEST TRƯỜNG HỢP ÍT TRANG (0 HOẶC 1 TRANG)
@pytest.mark.parametrize("current, total, expected", [
    (1, 0, []),  # 0 trang thì trả về list rỗng
    (1, 1, [1]),  # 1 trang
    (0, 0, []),  # Current page = 0 (dữ liệu rác)
    (-5, 1, [1]),  # Current page âm
], ids=["zero_pages", "one_page", "current_zero", "current_negative"])
def test_get_page_range_low_total_pages(current, total, expected):
    assert list(dao.get_page_range(current, total)) == expected


# TEST MẶC ĐỊNH (max_visible = 3)
# Bao phủ lề trái, giữa, lề phải và vượt biên
@pytest.mark.parametrize("current, total, expected", [
    (1, 5, [1, 2, 3]),  # Sát lề trái
    (2, 5, [1, 2, 3]),  # Gần lề trái (Bị tràn nên dịch phải)
    (3, 5, [2, 3, 4]),  # Ở giữa (Chuẩn)
    (4, 5, [3, 4, 5]),  # Gần lề phải (Bị tràn nên dịch trái)
    (5, 5, [3, 4, 5]),  # Sát lề phải
    (0, 5, [1, 2, 3]),  # Vượt biên: Current < 1
    (99, 5, [3, 4, 5]),  # Vượt biên: Current > total_pages
], ids=["left_edge", "near_left_edge", "middle", "near_right_edge", "right_edge", "out_of_bounds_low",
        "out_of_bounds_high"])
def test_get_page_range_default_visible_3(current, total, expected):
    assert list(dao.get_page_range(current, total)) == expected


# TEST TÙY CHỈNH MAX_VISIBLE (VD: 5)
@pytest.mark.parametrize("current, total, visible, expected", [
    (3, 10, 5, [1, 2, 3, 4, 5]),  # Vẫn chạm lề trái (3-2 = 1)
    (5, 10, 5, [3, 4, 5, 6, 7]),  # Ở giữa chuẩn
    (8, 10, 5, [6, 7, 8, 9, 10]),  # Chạm lề phải
], ids=["touch_left_edge", "middle_perfect", "touch_right_edge"])
def test_get_page_range_custom_visible(current, total, visible, expected):
    assert list(dao.get_page_range(current, total, max_visible=visible)) == expected


# TEST TRƯỜNG HỢP SỐ NÚT HIỂN THỊ LỚN HƠN TỔNG SỐ TRANG
@pytest.mark.parametrize("current, total, visible, expected", [
    (3, 3, 5, [1, 2, 3]),
    (2, 2, 10, [1, 2]),  # Muốn hiện 10 nút nhưng chỉ có 2 trang
], ids=["visible_exceeds_total_slightly", "visible_exceeds_total_greatly"])
def test_get_page_range_visible_exceeds_total(current, total, visible, expected):
    assert list(dao.get_page_range(current, total, max_visible=visible)) == expected
