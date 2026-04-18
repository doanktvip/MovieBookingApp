from unittest.mock import patch


# TRƯỜNG HỢP: GIẢI PHÓNG GHẾ THÀNH CÔNG
def test_api_release_seat_success(test_client):
    with test_client.session_transaction() as sess:
        sess['user_session_id'] = 'session-123'
        sess['booking'] = {
            "101": {"name": "A1", "price": 50000},
            "102": {"name": "A2", "price": 50000}
        }

    with patch('movieapp.dao.release_single_seat_db') as mocked_dao:
        response = test_client.post('/api/release-seat', json={"seat_id": 101})

        assert response.status_code == 200
        assert response.json["status"] == "success"

        mocked_dao.assert_called_once_with(101, 'session-123')

        with test_client.session_transaction() as sess:
            assert "101" not in sess['booking']
            assert "102" in sess['booking']


# TRƯỜNG HỢP: THIẾU DỮ LIỆU
def test_api_release_seat_missing_data(test_client):
    response = test_client.post('/api/release-seat', json={"seat_id": 101})

    assert response.status_code == 200
    with patch('movieapp.dao.release_single_seat_db') as mocked_dao:
        test_client.post('/api/release-seat', json={})
        mocked_dao.assert_not_called()
