from datetime import datetime, timedelta
from unittest.mock import patch
from movieapp import dao, db
from movieapp.models import ShowtimeSeat, Seat
from movieapp.test.conftest import test_app, test_session, sample_showtimes_complex, sample_movies_data, sample_cinemas, \
    sample_basic_setup


# Test trường hợp cập nhật thành công
def test_update_future_showtime_seats_price_success(test_app, sample_showtimes_complex):
    with test_app.app_context():
        # Lấy loại ghế VIP và suất chiếu từ fixture
        st_vip = sample_showtimes_complex["seat_types"]["vip"]
        showtime = sample_showtimes_complex["showtime"]

        # Đảm bảo suất chiếu nằm ở TƯƠNG LAI để thỏa mãn điều kiện lọc
        showtime.start_time = datetime.now() + timedelta(days=2)
        db.session.commit()

        # Thiết lập phụ phí mới
        new_surcharge = 50000.0

        # Gọi hàm DAO
        result = dao.update_future_showtime_seats_price(st_vip.id, new_surcharge)

        assert result is True

        # Công thức: base_price (50000) + new_surcharge (50000) = 100000
        updated_seat = ShowtimeSeat.query.join(Seat).filter(
            ShowtimeSeat.showtime_id == showtime.id,
            Seat.seat_type_id == st_vip.id
        ).first()

        assert float(updated_seat.price) == 100000.0


# Test trường hợp gặp lỗi
def test_update_future_showtime_seats_price_exception(test_app):
    with test_app.app_context():
        with patch.object(db.session, 'execute', side_effect=Exception("Lỗi quá trình")):
            result = dao.update_future_showtime_seats_price(1, 1000.0)
            assert result is False
