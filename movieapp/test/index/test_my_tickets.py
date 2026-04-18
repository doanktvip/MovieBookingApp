import pytest
from unittest.mock import patch, MagicMock
import math


# Giả lập trạng thái đã đăng nhập bằng user1
@pytest.fixture
def logged_in_client(test_client, sample_users):
    user = sample_users["users"]["user1"]
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    return test_client, user


def test_my_tickets_success(logged_in_client, test_app):
    client, user = logged_in_client

    page_size = test_app.config.get('PAGE_SIZE', 5)

    total_bookings = 12

    expected_total_pages = math.ceil(total_bookings / page_size)
    expected_range = range(1, expected_total_pages + 1)

    mock_bookings = [MagicMock(), MagicMock()]

    with patch('movieapp.dao.get_bookings_by_user') as mocked_get, \
            patch('movieapp.dao.count_bookings_by_user') as mocked_count, \
            patch('movieapp.dao.get_page_range') as mocked_range, \
            patch('movieapp.index.render_template') as mocked_render:
        mocked_get.return_value = mock_bookings
        mocked_count.return_value = total_bookings
        mocked_range.return_value = expected_range
        mocked_render.return_value = "Tickets Page"

        response = client.get('/tickets?page=2')

        assert response.status_code == 200

        mocked_get.assert_called_once_with(user_id=user.id, page=2)
        mocked_count.assert_called_once_with(user.id)

        mocked_range.assert_called_once_with(current_page=2, total_pages=expected_total_pages)

        mocked_render.assert_called_once_with(
            'ticket.html',
            bookings=mock_bookings,
            pages=expected_total_pages,
            page=2,
            page_range=expected_range
        )


# Test trường hợp người dùng chưa mua vé nào
def test_my_tickets_no_bookings(logged_in_client, test_app):
    client, user = logged_in_client

    with patch('movieapp.dao.count_bookings_by_user', return_value=0), \
            patch('movieapp.dao.get_bookings_by_user', return_value=[]), \
            patch('movieapp.dao.get_page_range', return_value=range(0)), \
            patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Empty"
        client.get('/tickets')

        _, kwargs = mocked_render.call_args
        assert kwargs['pages'] == 0
        assert kwargs['bookings'] == []
