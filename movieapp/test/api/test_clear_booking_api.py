from unittest.mock import patch


# TRƯỜNG HỢP: CÓ SESSION_ID VÀ DỌN DẸP THÀNH CÔNG
def test_clear_booking_session_success(test_client):
    with test_client.session_transaction() as sess:
        sess['user_session_id'] = 'active-session-123'
        sess['booking'] = {'1': 'seat1'}

    with patch('movieapp.dao.clear_db_booking_by_session') as mocked_clear_db:
        response = test_client.post('/api/clear-booking-session')

        assert response.status_code == 200
        assert response.json["status"] == "cleared"

        mocked_clear_db.assert_called_once_with('active-session-123')

        with test_client.session_transaction() as sess:
            assert 'booking' not in sess


# TRƯỜNG HỢP: DAO GẶP LỖI
def test_clear_db_booking_dao_exception(test_app):
    from movieapp.dao import clear_db_booking_by_session

    with test_app.app_context():
        with patch('movieapp.models.ShowtimeSeat.query') as mocked_query:
            mocked_query.filter_by.side_effect = Exception("Database Connection Error")

            clear_db_booking_by_session('fail-session')
