import pytest
from unittest.mock import patch, MagicMock
from movieapp import dao, db
from movieapp.models import User
# Import các fixture từ test_base
from movieapp.test.test_base import test_app, test_session, sample_users


# 1. Test không tìm thấy người dùng
def test_update_user_profile_not_found(test_app):
    with test_app.app_context():
        # Dùng ID không tồn tại
        success, msg = dao.update_user_profile(999, "new@gmail.com")
        assert success is False
        assert msg == "Không tìm thấy người dùng!"


# Test trùng Email với người khác
def test_update_user_profile_email_taken(test_app, sample_users):
    with test_app.app_context():
        u1 = sample_users["users"]["user1"]
        u2 = sample_users["users"]["user2"]

        # Thử cập nhật email của u1 thành email của u2
        success, msg = dao.update_user_profile(u1.id, u2.email)

        assert success is False
        assert "đã được sử dụng" in msg


# Test lỗi khi upload ảnh
def test_update_user_profile_upload_fail(test_app, sample_users):
    with test_app.app_context():
        u1 = sample_users["users"]["user1"]
        mock_file = MagicMock()
        mock_file.filename = 'avatar.jpg'

        # Giả lập hàm upload_image trả về None
        with patch('movieapp.dao.upload_image', return_value=None):
            success, msg = dao.update_user_profile(u1.id, "new@gmail.com", mock_file)

            assert success is False
            assert "Lỗi khi tải ảnh lên" in msg


# Test cập nhật thành công cả Email và Avatar
def test_update_user_profile_success(test_app, sample_users):
    with test_app.app_context():
        u1 = db.session.merge(sample_users["users"]["user1"])
        mock_file = MagicMock()
        mock_file.filename = 'new_avatar.png'
        new_email = "updated_email@gmail.com"
        new_url = "http://cloudinary.com/new_avatar.png"

        # Giả lập upload thành công
        with patch('movieapp.dao.upload_image', return_value=new_url):
            success, msg = dao.update_user_profile(u1.id, new_email, mock_file)

            assert success is True
            # Kiểm tra dữ liệu trong DB
            db.session.refresh(u1)
            assert u1.email == new_email
            assert u1.avatar == new_url


# Test lỗi Database khi commit
def test_update_user_profile_db_error(test_app, sample_users):
    with test_app.app_context():
        u1 = db.session.merge(sample_users["users"]["user1"])

        # Giả lập lỗi commit
        with patch.object(db.session, 'commit', side_effect=Exception("Commit Failed")):
            success, msg = dao.update_user_profile(u1.id, "valid@gmail.com")

            assert success is False
            assert "Commit Failed" in msg
