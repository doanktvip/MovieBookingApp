from movieapp.admin import CinemaView


# TEST: _format_map_url (CinemaView)
def test_cinema_format_map_url_coverage():
    class DummyModel:
        pass

    m = DummyModel()

    # Nhánh 1: Không có link bản đồ
    m.map_url = None
    # Truy cập thẳng vào hàm của class CinemaView
    result_empty = CinemaView._format_map_url(view=None, context=None, model=m, name='map_url')
    assert result_empty == ''

    # Nhánh 2: Có link bản đồ
    m.map_url = 'https://maps.google.com/test_location'
    result_has_url = CinemaView._format_map_url(view=None, context=None, model=m, name='map_url')

    # Kiểm tra xem mã HTML trả về có chứa link và thẻ <a> không
    assert 'https://maps.google.com/test_location' in result_has_url
    assert '<a href=' in result_has_url
    assert 'target="_blank"' in result_has_url


# TEST: on_model_change (CinemaView)
def test_cinema_on_model_change_coverage():
    # Tạo một class giả lập thông tin Rạp chiếu
    class DummyCinema:
        def __init__(self):
            self.name = None
            self.address = None
            self.map_url = None

    # Nhánh 1: Có đầy đủ Tên và Địa chỉ
    m1 = DummyCinema()
    m1.name = "CGV"
    m1.address = "Quận 1 HCM"

    # GỌI TRỰC TIẾP HÀM QUA CLASS (Không cần khởi tạo View)
    CinemaView.on_model_change(self=None, form=None, model=m1, is_created=True)

    # Kiểm tra xem map_url có được tự động tạo không
    assert m1.map_url is not None
    assert "CGV" in m1.map_url
    assert "Quận+1+HCM" in m1.map_url

    # Nhánh 2: Bị thiếu Địa chỉ
    m2 = DummyCinema()
    m2.name = "Galaxy"
    m2.address = ""  # Thiếu địa chỉ

    # GỌI TRỰC TIẾP HÀM QUA CLASS
    CinemaView.on_model_change(self=None, form=None, model=m2, is_created=True)

    # Do thiếu thông tin nên map_url vẫn giữ nguyên là None
    assert m2.map_url is None
