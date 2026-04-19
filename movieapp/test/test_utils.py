from datetime import datetime
import pytest
from movieapp.utils import stats_seats, format_api_response_fail, get_vn_weekday


# TEST HÀM stats_seats
# Nhánh 1: Giỏ hàng (booking) trống (là None hoặc dict rỗng)
def test_stats_seats_empty():
    result_none = stats_seats(None)
    assert result_none['seats'] == []
    assert result_none['total_amount'] == 0

    result_empty_dict = stats_seats({})
    assert result_empty_dict['seats'] == []
    assert result_empty_dict['total_amount'] == 0


# Nhánh 2: Giỏ hàng có dữ liệu ghế
def test_stats_seats_with_data():
    mock_booking = {
        'A1': {'seat_id': 1, 'price': 50000},
        'A2': {'seat_id': 2, 'price': '75000'},  # Cố tình truyền String để test hàm float()
        'A3': {'seat_id': 3}  # Cố tình thiếu key 'price' để test get('price', 0)
    }

    result = stats_seats(mock_booking)

    # Kiểm tra xem danh sách ghế có lấy đủ 3 phần tử không
    assert len(result['seats']) == 3
    assert result['seats'][0]['seat_id'] == 1

    # Kiểm tra tổng tiền (50000 + 75000 + 0 = 125000.0)
    assert result['total_amount'] == 125000.0


# TEST HÀM format_api_response_fail
def test_format_api_response_fail():
    # Nhánh 1: Dùng status mặc định ('error')
    res_default = format_api_response_fail("Có lỗi xảy ra")
    assert res_default['status'] == 'error'

    # Nhánh 2: Truyền status tùy chỉnh ('fail')
    res_custom = format_api_response_fail("Dữ liệu không hợp lệ", status="fail")
    assert res_custom['status'] == 'fail'


# TEST HÀM get_vn_weekday
# Kiểm tra hàm chuyển đổi ngày sang định dạng thứ tiếng Việt.
@pytest.mark.parametrize("date_str, expected_vn_day", [
    ("2026-04-13", "T2"),  # Thứ Hai
    ("2026-04-14", "T3"),  # Thứ Ba
    ("2026-04-15", "T4"),  # Thứ Tư
    ("2026-04-16", "T5"),  # Thứ Năm
    ("2026-04-17", "T6"),  # Thứ Sáu
    ("2026-04-18", "T7"),  # Thứ Bảy
    ("2026-04-19", "CN"),  # Chủ Nhật
])
def test_get_vn_weekday_logic(date_str, expected_vn_day):
    test_date = datetime.strptime(date_str, "%Y-%m-%d")

    result = get_vn_weekday(test_date)

    assert result == expected_vn_day


# Kiểm tra xem hàm có báo lỗi khi truyền sai kiểu dữ liệu không
def test_get_vn_weekday_with_invalid_type():
    with pytest.raises(AttributeError):
        # Truyền vào một chuỗi thay vì object datetime
        get_vn_weekday("2026-04-18")
