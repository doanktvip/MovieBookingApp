import pytest
from movieapp import dao, db
from movieapp.models import Province
from unittest.mock import patch
from movieapp.test.conftest import test_app, test_session


# Test trường hợp tên rỗng
@pytest.mark.parametrize("invalid_name", ["", "   ", None])
def test_get_or_create_province_empty_name(test_app, invalid_name):
    with test_app.app_context():
        if invalid_name is None:
            with pytest.raises(AttributeError):
                dao.get_or_create_province(None)
        else:
            result = dao.get_or_create_province(invalid_name)
            assert result is None


# Test trường hợp tỉnh đã tồn tại (Lấy từ DB)
def test_get_or_create_province_exists(test_app):
    with test_app.app_context():
        # Tạo sẵn dữ liệu
        p = Province(name="Lâm Đồng")
        db.session.add(p)
        db.session.commit()

        # Gọi hàm với tên đã có
        result = dao.get_or_create_province("  Lâm Đồng  ")

        assert result.id == p.id
        assert result.name == "Lâm Đồng"
        assert Province.query.count() == 1


# Test trường hợp tạo mới thành công
def test_get_or_create_province_create_new(test_app):
    with test_app.app_context():
        # Đảm bảo ban đầu chưa có
        assert Province.query.filter_by(name="Cần Thơ").first() is None

        result = dao.get_or_create_province("Cần Thơ")

        assert result is not None
        assert result.name == "Cần Thơ"
        assert Province.query.count() == 1


# Test trường hợp lỗi Database
def test_get_or_create_province_exception(test_app):
    with test_app.app_context():
        # Mock lệnh commit để ném ra lỗi
        with patch.object(db.session, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception) as excinfo:
                dao.get_or_create_province("Vũng Tàu")

            assert "DB Error" in str(excinfo.value)
            db.session.rollback()
            assert Province.query.filter_by(name="Vũng Tàu").first() is None
