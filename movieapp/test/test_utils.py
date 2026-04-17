from movieapp.utils import stats_seats, format_api_response_fail


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
