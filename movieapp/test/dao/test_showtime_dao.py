import pytest
from movieapp import dao
from movieapp.test.conftest import test_app, sample_showtimes_complex, sample_movies_data, sample_cinemas, \
    test_session, sample_basic_setup


# TEST HÀM: get_showtime_by_id
@pytest.mark.parametrize("use_valid_id, expected_found", [
    (True, True),  # TH1: Truyền ID hợp lệ -> Phải tìm thấy
    (False, False)  # TH2: Truyền ID không tồn tại (9999) -> Trả về None
], ids=["valid_showtime_id", "invalid_showtime_id"])
def test_get_showtime_by_id(test_app, sample_showtimes_complex, use_valid_id, expected_found):
    with test_app.app_context():
        valid_id = sample_showtimes_complex["showtime"].id
        target_id = valid_id if use_valid_id else 99999

        # Thực thi hàm
        result = dao.get_showtime_by_id(target_id)

        # Kiểm tra kết quả
        if expected_found:
            assert result is not None
            assert result.id == valid_id
        else:
            assert result is None


# TEST HÀM: get_seats_by_showtime
@pytest.mark.parametrize("use_valid_id, expected_empty", [
    (True, False),  # TH1: ID hợp lệ -> Trả về danh sách ghế
    (False, True)  # TH2: ID sai -> Trả về mảng rỗng []
], ids=["valid_showtime_seats", "invalid_showtime_seats"])
def test_get_seats_by_showtime(test_app, sample_showtimes_complex, use_valid_id, expected_empty):
    with test_app.app_context():
        valid_id = sample_showtimes_complex["showtime"].id
        target_id = valid_id if use_valid_id else 99999

        seats = dao.get_seats_by_showtime(target_id)

        if expected_empty:
            assert isinstance(seats, list)
            assert len(seats) == 0
        else:
            assert isinstance(seats, list)
            assert len(seats) > 0

            assert hasattr(seats[0], 'seat_id')
            assert hasattr(seats[0], 'status')

            for i in range(len(seats) - 1):
                current_seat = seats[i].seat
                next_seat = seats[i + 1].seat

                assert current_seat.row <= next_seat.row

                if current_seat.row == next_seat.row:
                    assert current_seat.col < next_seat.col


def test_get_seats_all(test_app, sample_movies_data):
    with test_app.app_context():
        seats = dao.get_seats_all()

        assert isinstance(seats, list)
        assert len(seats) > 0

        expected_min_length = len(sample_movies_data["seats"])
        assert len(seats) >= expected_min_length


# TEST HÀM: get_seat_type
@pytest.mark.parametrize("use_valid_id, expected_found", [
    (True, True),  # TH1: ID hợp lệ -> Phải tìm thấy
    (False, False)  # TH2: ID không tồn tại -> Trả về None
], ids=["valid_seat_type_id", "invalid_seat_type_id"])
def test_get_seat_type(test_app, sample_movies_data, use_valid_id, expected_found):
    with test_app.app_context():
        valid_id = sample_movies_data["seats"][0].seat_type_id
        target_id = valid_id if use_valid_id else 99999

        # Thực thi hàm
        result = dao.get_seat_type(target_id)

        if expected_found:
            assert result is not None
            assert result.id == valid_id
        else:
            assert result is None


# TEST HÀM: get_seat_by_id
@pytest.mark.parametrize("use_valid_id, expected_found", [
    (True, True),  # TH1: ID hợp lệ -> Phải tìm thấy
    (False, False)  # TH2: ID không tồn tại -> Trả về None
], ids=["valid_seat_id", "invalid_seat_id"])
def test_get_seat_by_id(test_app, sample_movies_data, use_valid_id, expected_found):
    with test_app.app_context():
        valid_id = sample_movies_data["seats"][0].id
        target_id = valid_id if use_valid_id else 99999

        result = dao.get_seat_by_id(target_id)

        if expected_found:
            assert result is not None
            assert result.id == valid_id
        else:
            assert result is None
