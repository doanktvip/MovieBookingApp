import pytest
from flask import url_for
from flask_login import current_user, login_user


# Kiểm tra xem người dùng có đăng xuất thành công và được chuyển hướng không.
def test_logout_my_user_success(test_app, test_client, sample_users):
    user = sample_users["users"]["user1"]

    # Thiết lập ngữ cảnh yêu cầu để đăng nhập user trước khi test logout
    with test_app.test_request_context():
        # Đăng nhập giả lập để current_user được thiết lập
        login_user(user)
        assert current_user.is_authenticated is True

        # Sử dụng test_client để gửi request đến route logout
        response = test_client.get("/logout", follow_redirects=False)

        # Kiểm tra mã trạng thái chuyển hướng (302 Found)
        assert response.status_code == 302

        # Kiểm tra xem có redirect về trang chủ không
        assert response.location == url_for('index', _external=False) or response.location == "/"
        # Kiểm tra xem current_user đã bị xóa (is_anonymous) chưa
        assert current_user.is_authenticated is False
