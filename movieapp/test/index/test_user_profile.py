import pytest
from unittest.mock import patch


# Fixture giả lập login để vượt qua @login_user_required."
@pytest.fixture
def logged_in_client(test_client, sample_users):
    user = sample_users["users"]["user1"]
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    return test_client, user


#  TEST RENDER TRANG USERINFO
def test_userinfo_route(logged_in_client):
    client, _ = logged_in_client
    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Profile Page"
        response = client.get('/userinfo')

        assert response.status_code == 200
        mocked_render.assert_called_once_with("userinfo.html")


# TEST CẬP NHẬT PROFILE THÀNH CÔNG
def test_edit_profile_success(logged_in_client):
    client, user = logged_in_client
    with patch('movieapp.dao.update_user_profile') as mocked_update:
        mocked_update.return_value = (True, "Cập nhật thành công!")

        response = client.post('/edit-profile', data={
            'email': 'newemail@gmail.com'
        }, content_type='multipart/form-data')

        # Kiểm tra redirect về trang userinfo
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/userinfo')
        mocked_update.assert_called_once()


# TEST CẬP NHẬT PROFILE THẤT BẠ
def test_edit_profile_fail(logged_in_client):
    client, _ = logged_in_client
    with patch('movieapp.dao.update_user_profile') as mocked_update:
        mocked_update.return_value = (False, "Email đã tồn tại!")

        response = client.post('/edit-profile', data={'email': 'existed@gmail.com'})

        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert '_flashes' in sess


# TEST ĐỔI MẬT KHẨU: XÁC NHẬN KHÔNG KHỚP
def test_change_password_mismatch(logged_in_client):
    client, _ = logged_in_client
    response = client.post('/change-password', data={
        'old_password': '123',
        'new_password': 'abc',
        'confirm_password': 'xyz'  # Không khớp
    })

    assert response.status_code == 302
    # Đảm bảo DAO không bị gọi khi dữ liệu đầu vào sai ngay tại Route
    with patch('movieapp.dao.change_password') as mocked_change:
        client.post('/change-password', data={'new_password': '1', 'confirm_password': '2'})
        mocked_change.assert_not_called()


# TEST ĐỔI MẬT KHẨU: THÀNH CÔNG
def test_change_password_success(logged_in_client):
    client, user = logged_in_client
    with patch('movieapp.dao.change_password') as mocked_change:
        mocked_change.return_value = (True, "Đổi mật khẩu thành công!")

        response = client.post('/change-password', data={
            'old_password': 'old_pass_123',
            'new_password': 'new_pass_456',
            'confirm_password': 'new_pass_456'
        })

        assert response.status_code == 302
        mocked_change.assert_called_once_with(user.id, 'old_pass_123', 'new_pass_456')


# TEST ĐỔI MẬT KHẨU: SAI MẬT KHẨU CŨ
def test_change_password_wrong_old(logged_in_client):
    client, _ = logged_in_client
    with patch('movieapp.dao.change_password') as mocked_change:
        mocked_change.return_value = (False, "Mật khẩu cũ không đúng!")

        response = client.post('/change-password', data={
            'old_password': 'wrong',
            'new_password': 'new',
            'confirm_password': 'new'
        })

        assert response.status_code == 302
        mocked_change.assert_called_once()
