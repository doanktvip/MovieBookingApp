import pytest
from unittest.mock import patch


# Fixture giả lập login để vượt qua Decorator
@pytest.fixture
def mock_user_session(test_client, sample_users):
    user = sample_users["users"]["user1"]
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['user_session_id'] = 'session-id-123'
    return user


# TRƯỜNG HỢP: SUẤT CHIẾU ĐÃ BẮT ĐẦU
def test_api_booking_movie_started(test_client, mock_user_session):
    with patch('movieapp.dao.process_seat_reservations_secure') as mocked_dao:
        mocked_dao.return_value = (False, "Phim đã bắt đầu chiếu, không thể đặt vé.", {}, None)

        response = test_client.post('/api/booking', json={
            "showtime_id": 1,
            "seats": [{"id": "101", "name": "A1"}]
        })

        assert response.status_code == 400
        assert "Phim đã bắt đầu chiếu" in response.json["message"]


# TRƯỜNG HỢP: VƯỢT QUÁ 8 VÉ
def test_api_booking_limit_exceeded(test_client, mock_user_session):
    with patch('movieapp.dao.process_seat_reservations_secure') as mocked_dao:
        error_msg = "Bạn đã có 6 vé cho suất này. Chỉ được đặt tối đa 8 ghế."
        mocked_dao.return_value = (False, error_msg, {}, None)

        response = test_client.post('/api/booking', json={
            "showtime_id": 1,
            "seats": [{"id": "101", "name": "A1"}, {"id": "102", "name": "A2"}]
        })

        assert response.status_code == 400
        assert response.json["message"] == error_msg


# TRƯỜNG HỢP: GHẾ VỪA CÓ NGƯỜI CHỌ
def test_api_booking_seat_taken(test_client, mock_user_session):
    with patch('movieapp.dao.process_seat_reservations_secure') as mocked_dao:
        mocked_dao.return_value = (False, "Ghế A5 vừa có người khác nhanh tay chọn mất.", {}, None)

        response = test_client.post('/api/booking', json={
            "showtime_id": 1,
            "seats": [{"id": "105", "name": "A5"}]
        })

        assert response.status_code == 400
        assert "nhanh tay chọn mất" in response.json["message"]


# TRƯỜNG HỢP: GHẾ KHÔNG HỢP LỆ
def test_api_booking_invalid_seats(test_client, mock_user_session):
    with patch('movieapp.dao.process_seat_reservations_secure') as mocked_dao:
        mocked_dao.return_value = (False, "Một số ghế không hợp lệ hoặc không thuộc suất chiếu này.", {}, None)

        response = test_client.post('/api/booking', json={
            "showtime_id": 1,
            "seats": [{"id": "999", "name": "X1"}]
        })

        assert response.status_code == 400
        assert "không hợp lệ" in response.json["message"]


# TRƯỜNG HỢP: THÀNH CÔNG
def test_api_booking_flow_success(test_client, mock_user_session):
    booking_dict = {"101": {"id": "101", "name": "A1", "price": 85000.0}}
    with patch('movieapp.dao.process_seat_reservations_secure') as mocked_dao:
        mocked_dao.return_value = (True, "Giữ ghế thành công", booking_dict, "2026-04-18 09:00:00")

        response = test_client.post('/api/booking', json={
            "showtime_id": 1,
            "seats": [{"id": "101", "name": "A1"}]
        })

        assert response.status_code == 200
        assert response.json["status"] == "success"
        with test_client.session_transaction() as sess:
            assert sess['booking'] == booking_dict


# Trường hợp thiếu showtime_id
def test_api_booking_missing_showtime_id(test_client, mock_user_session):
    response = test_client.post('/api/booking', json={
        "seats": [{"id": "101", "name": "A1"}]
    })

    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert response.json["message"] == "Vui lòng chọn ít nhất 1 ghế!"


# Trường hợp danh sách seats rỗng
def test_api_booking_empty_seats(test_client, mock_user_session):
    response = test_client.post('/api/booking', json={
        "showtime_id": 1,
        "seats": []
    })

    assert response.status_code == 400
    assert response.json["message"] == "Vui lòng chọn ít nhất 1 ghế!"
