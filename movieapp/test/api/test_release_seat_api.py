from unittest.mock import patch, MagicMock

from movieapp.models import UserRole


# TRƯỜNG HỢP: GIẢI PHÓNG GHẾ THÀNH CÔNG
def test_api_release_seat_success(test_client):
    with test_client.session_transaction() as sess:
        sess['user_session_id'] = 'session-123'
        sess['booking'] = {
            "101": {"name": "A1", "price": 50000},
            "102": {"name": "A2", "price": 50000}
        }

    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.role = UserRole.USER
    with patch('movieapp.decorators.current_user', mock_user):
        with patch('movieapp.dao.release_single_seat_db') as mocked_dao:
            response = test_client.post('/api/release-seat', json={"seat_id": 101})

            assert response.status_code == 200
            assert response.json["status"] == "success"

            mocked_dao.assert_called_once_with(101, 'session-123')

            with test_client.session_transaction() as sess:
                assert "101" not in sess['booking']
                assert "102" in sess['booking']


from unittest.mock import patch, MagicMock
from movieapp.models import UserRole


# TRƯỜNG HỢP: THIẾU DỮ LIỆU
def test_api_release_seat_missing_data(test_client):
    # Giả lập một User hợp lệ (đã đăng nhập, quyền USER)
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.role = UserRole.USER

    # Vượt qua decorator bảo mật
    with patch('movieapp.decorators.current_user', mock_user):
        # Test 1: Có gửi seat_id nhưng bị thiếu Session ID (khách không có session)
        response1 = test_client.post('/api/release-seat', json={"seat_id": 101})
        assert response1.status_code == 200
        assert response1.json["status"] == "success"

        # Test 2: Kiểm tra chắc chắn rằng DAO (Database) KHÔNG BỊ GỌI khi thiếu dữ liệu (gửi json rỗng)
        with patch('movieapp.dao.release_single_seat_db') as mocked_dao:
            response2 = test_client.post('/api/release-seat', json={})

            assert response2.status_code == 200
            mocked_dao.assert_not_called()  # Chắc chắn DAO chưa được kích hoạt
