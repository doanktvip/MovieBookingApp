import hashlib
from unittest.mock import patch
from movieapp import dao, db


# 1. Test không tìm thấy người dùng
def test_change_password_user_not_found(test_app):
    with test_app.app_context():
        # Dùng ID không tồn tại
        success, msg = dao.change_password(999, "old123", "new123")
        assert success is False
        assert msg == "Người dùng không tồn tại!"


# Test mật khẩu cũ không chính xác
def test_change_password_wrong_old_pass(test_app, sample_users):
    with test_app.app_context():
        u1 = sample_users["users"]["user1"]
        # Mật khẩu thật trong fixture là '123456', ta thử bằng 'wrongpass'
        success, msg = dao.change_password(u1.id, "wrongpass", "new_pass_123")

        assert success is False
        assert msg == "Mật khẩu cũ không chính xác!"


# Test đổi mật khẩu thành công
def test_change_password_success(test_app, sample_users):
    with test_app.app_context():
        u1 = db.session.merge(sample_users["users"]["user1"])
        old_pass = "123456"
        new_pass = "new_secure_pass"

        success, msg = dao.change_password(u1.id, old_pass, new_pass)

        assert success is True
        assert msg == "Đổi mật khẩu thành công!"

        # Kiểm tra mật khẩu mới đã được lưu và băm MD5 đúng chưa
        db.session.refresh(u1)
        expected_hash = hashlib.md5(new_pass.encode('utf-8')).hexdigest()
        assert u1.password == expected_hash


# Test lỗi Database khi commit
def test_change_password_db_error(test_app, sample_users):
    with test_app.app_context():
        u1 = db.session.merge(sample_users["users"]["user1"])

        # Giả lập lỗi commit để nhảy vào khối except
        with patch.object(db.session, 'commit', side_effect=Exception("Kết nối database thất bại")):
            success, msg = dao.change_password(u1.id, "123456", "newpass")

            assert success is False
            assert "Kết nối database thất bại" in msg
