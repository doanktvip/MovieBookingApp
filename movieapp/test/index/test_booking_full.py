from unittest.mock import patch
from datetime import datetime, timedelta


# TEST CHẶN TRUY CẬP
def test_booking_auth_required(test_client):
    with patch('flask_login.utils._get_user') as mocked_user:
        # Giả lập một user chưa đăng nhập (is_authenticated = False)
        mocked_user.return_value.is_authenticated = False
        # Nếu decorator của bạn truy cập .role, ta tạo mock cho nó luôn để không crash
        mocked_user.return_value.role = None

        response = test_client.get('/booking/showtime-1-slug-room-1')
        assert response.status_code in [302, 403, 401]


# TEST LỖI 404 (Suất chiếu không tồn tại hoặc sai phòng)
def test_booking_404_not_found(test_client, sample_users):
    user = sample_users["users"]["user1"]
    with patch('flask_login.utils._get_user') as mocked_user:
        mocked_user.return_value = user

        res1 = test_client.get('/booking/showtime-9999-slug-room-1')
        assert res1.status_code == 404


# TEST EXCEPTION
def test_booking_release_seats_exception(test_client, sample_full_chain):
    user = sample_full_chain["users"]["user1"]
    st = sample_full_chain["showtime"]

    with patch('flask_login.utils._get_user') as mocked_user:
        mocked_user.return_value = user
        with patch('movieapp.dao.release_expired_seats') as mocked_release:
            mocked_release.side_effect = [Exception("DB Busy"), None]

            with patch('movieapp.index.render_template') as mocked_render:
                mocked_render.return_value = "OK"
                url = f'/booking/showtime-{st.id}-slug-room-{st.room_id}'
                response = test_client.get(url)

                assert response.status_code == 200
                with test_client.session_transaction() as sess:
                    assert any("Hệ thống đang bận" in m[1] for m in sess.get('_flashes', []))


# TEST KHI GIỮ GHẾ CÒN HẠN
def test_booking_session_active(test_client, sample_full_chain):
    user = sample_full_chain["users"]["user1"]
    st = sample_full_chain["showtime"]
    future_time = datetime.now() + timedelta(minutes=5)

    with patch('flask_login.utils._get_user') as mocked_user:
        mocked_user.return_value = user
        with test_client.session_transaction() as sess:
            sess['user_session_id'] = 'active_sid'

        with patch('movieapp.dao.get_reservation_expiry_time') as mocked_expire:
            mocked_expire.return_value = future_time
            with patch('movieapp.index.render_template') as mocked_render:
                mocked_render.return_value = "OK"

                test_client.get(f'/booking/showtime-{st.id}-slug-room-{st.room_id}')

                call_kwargs = mocked_render.call_args.kwargs
                assert call_kwargs['time_remaining'] > 0
                assert call_kwargs['time_remaining'] <= 300


# TEST KHI GIỮ GHẾ HẾT HẠN
def test_booking_session_expired(test_client, sample_full_chain):
    user = sample_full_chain["users"]["user1"]
    st = sample_full_chain["showtime"]

    with patch('flask_login.utils._get_user') as mocked_user:
        mocked_user.return_value = user
        with test_client.session_transaction() as sess:
            sess['user_session_id'] = 'expired_sid'
            sess['booking'] = {'1': 'seat1'}  # Giả lập có dữ liệu cũ

        with patch('movieapp.dao.get_reservation_expiry_time') as mocked_expire:
            # Trả về None nghĩa là hết hạn hoặc không tìm thấy
            mocked_expire.return_value = None
            with patch('movieapp.index.render_template') as mocked_render:
                mocked_render.return_value = "OK"

                test_client.get(f'/booking/showtime-{st.id}-slug-room-{st.room_id}')

                # Kiểm tra session đã bị xóa chưa
                with test_client.session_transaction() as sess:
                    assert 'booking' not in sess

                call_kwargs = mocked_render.call_args.kwargs
                assert call_kwargs['booking_session'] == {}
                assert call_kwargs['time_remaining'] == 0


# TEST LOGIC TẠO SEAT_MAP
def test_booking_seat_map_logic(test_client, sample_full_chain):
    user = sample_full_chain["users"]["user1"]
    st = sample_full_chain["showtime"]

    with patch('flask_login.utils._get_user') as mocked_user:
        mocked_user.return_value = user
        with patch('movieapp.index.render_template') as mocked_render:
            mocked_render.return_value = "OK"

            test_client.get(f'/booking/showtime-{st.id}-slug-room-{st.room_id}')

            call_kwargs = mocked_render.call_args.kwargs
            seat_map = call_kwargs['seat_map']

            assert 'A' in seat_map
            assert 1 in seat_map['A']
