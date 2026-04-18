import pytest
from unittest.mock import patch


def test_common_attribute_logic(test_app):
    """Kiểm tra logic của common_attribute lấy từ app context processors."""
    # Tìm hàm trong danh sách đăng ký của Flask
    common_attr_func = None
    for func in test_app.template_context_processors[None]:
        if func.__name__ == 'common_attribute':
            common_attr_func = func
            break

    with test_app.app_context():
        # Patch tại module dao để đảm bảo bắt được cuộc gọi
        with patch('movieapp.dao.release_expired_seats') as mocked_release:
            result = common_attr_func()

            # Xác nhận hàm dọn dẹp ghế đã được gọi
            mocked_release.assert_called_once()

            # Xác nhận dữ liệu trả về cho template
            assert "slugify" in result
            assert callable(result["slugify"])
