import pytest
from unittest.mock import patch


# Giả lập trạng thái đã đăng nhập bằng user1.
@pytest.fixture
def logged_in_client(test_client, sample_users):
    """Giả lập trạng thái đã đăng nhập bằng user1."""
    user = sample_users["users"]["user1"]
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    return test_client, user


# TRƯỜNG HỢP: HỦY VÉ THÀNH CÔNG
def test_cancel_booking_success(logged_in_client):
    client, user = logged_in_client
    booking_id = 99

    with patch('movieapp.dao.cancel_booking') as mocked_cancel:
        mocked_cancel.return_value = (True, "Hủy đặt vé thành công!")

        response = client.post(f'/cancel-booking/{booking_id}')

        assert response.status_code == 302
        assert response.headers['Location'].endswith('/tickets')

        mocked_cancel.assert_called_once_with(booking_id=booking_id, user_id=user.id)

        with client.session_transaction() as sess:
            flash_messages = sess['_flashes']
            assert flash_messages[0][0] == "success"
            assert "Hủy đặt vé thành công" in flash_messages[0][1]


# TRƯỜNG HỢP: HỦY VÉ THẤT BẠI
def test_cancel_booking_fail(logged_in_client):
    client, user = logged_in_client
    booking_id = 100

    with patch('movieapp.dao.cancel_booking') as mocked_cancel:
        error_msg = "Không thể hủy vé đã quá hạn hoặc đã check-in."
        mocked_cancel.return_value = (False, error_msg)

        response = client.post(f'/cancel-booking/{booking_id}')

        assert response.status_code == 302

        with client.session_transaction() as sess:
            flash_messages = sess['_flashes']
            assert flash_messages[0][0] == "danger"
            assert flash_messages[0][1] == error_msg


# TRƯỜNG HỢP: CHƯA ĐĂNG NHẬP
def test_cancel_booking_unauthorized(test_client):
    response = test_client.post('/cancel-booking/99')
    assert response.status_code == 302
