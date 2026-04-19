from unittest.mock import patch
from movieapp.admin import SeatTypeView


# TEST: after_model_change (SeatTypeView)
@patch('movieapp.admin.dao.update_future_showtime_seats_price')
def test_seat_type_after_model_change_coverage(mock_update):
    # Tạo một model giả lập Loại ghế (SeatType)
    class DummySeatType:
        def __init__(self):
            self.id = 1
            self.surcharge = 50000

    m = DummySeatType()

    # Nhánh 1: is_created = True
    SeatTypeView.after_model_change(self=None, form=None, model=m, is_created=True)
    mock_update.assert_not_called()

    # Nhánh 2: is_created = False và Update Thành Công
    # Giả lập DAO trả về True
    mock_update.return_value = True
    SeatTypeView.after_model_change(self=None, form=None, model=m, is_created=False)
    # Đảm bảo DAO được gọi đúng với ID và Phụ thu của Model
    mock_update.assert_called_with(1, 50000)

    # Reset lại bộ đếm của Mock để chuẩn bị test nhánh 3
    mock_update.reset_mock()

    # Nhánh 3: is_created = False (Cập nhật) và Update Thất Bại
    # Giả lập DAO bị lỗi, trả về False
    mock_update.return_value = False
    SeatTypeView.after_model_change(self=None, form=None, model=m, is_created=False)
    # Đảm bảo DAO vẫn được gọi, và code chạy trót lọt qua dòng `pass` mà không bị crash
    mock_update.assert_called_with(1, 50000)
