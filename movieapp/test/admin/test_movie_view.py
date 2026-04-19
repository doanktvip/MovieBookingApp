from unittest.mock import MagicMock, patch
from movieapp.admin import MovieView


# TEST: on_model_change (MovieView)
@patch('movieapp.admin.dao.upload_image')
def test_movie_on_model_change_coverage(mock_upload):
    # Tạo một model giả lập Phim
    class DummyMovie:
        def __init__(self):
            self.image = "anh_mac_dinh.png"

    m = DummyMovie()

    # Nhánh 1: Form có ảnh và Upload THÀNH CÔNG
    mock_form_success = MagicMock()
    mock_form_success.upload_image.data = "file_anh_gia_lap.jpg"
    # Giả lập Cloudinary trả về một link ảnh
    mock_upload.return_value = "http://cloudinary.com/phimm_moi.jpg"

    MovieView.on_model_change(self=None, form=mock_form_success, model=m, is_created=True)

    # Đảm bảo hàm upload được gọi với đúng thư mục "movies"
    mock_upload.assert_called_once_with("file_anh_gia_lap.jpg", folder_name="movies")
    # Đảm bảo thuộc tính ảnh của phim được cập nhật link mới
    assert m.image == "http://cloudinary.com/phimm_moi.jpg"

    mock_upload.reset_mock()  # Reset bộ đếm mock

    # Nhánh 2: Form có ảnh nhưng Upload THẤT BẠI
    m.image = "anh_cu.png"  # Khôi phục lại một ảnh cũ
    mock_form_fail = MagicMock()
    mock_form_fail.upload_image.data = "file_loi.jpg"
    # Giả lập Cloudinary bị lỗi, trả về None
    mock_upload.return_value = None

    MovieView.on_model_change(self=None, form=mock_form_fail, model=m, is_created=True)

    # Hàm upload vẫn được gọi, nhưng do lỗi nên vòng 'if image_url:' không chạy
    mock_upload.assert_called_once_with("file_loi.jpg", folder_name="movies")
    # Thuộc tính ảnh giữ nguyên, không bị ghi đè
    assert m.image == "anh_cu.png"

    mock_upload.reset_mock()

    # Nhánh 3: Form KHÔNG có ảnh nào được tải lên
    mock_form_empty = MagicMock()
    mock_form_empty.upload_image.data = None

    MovieView.on_model_change(self=None, form=mock_form_empty, model=m, is_created=True)

    # Do không có ảnh, hàm upload không bao giờ được gọi
    mock_upload.assert_not_called()
