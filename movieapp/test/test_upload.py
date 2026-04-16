import pytest
from unittest.mock import patch, MagicMock
from movieapp import dao


# Test trường hợp không có file
def test_upload_image_no_file():
    result = dao.upload_image(None)
    assert result is None


# Test trường hợp upload thành công
def test_upload_image_success():
    mock_file = MagicMock()
    mock_response = {'secure_url': 'https://cloudinary.com/my-image.jpg'}

    with patch('cloudinary.uploader.upload', return_value=mock_response):
        result = dao.upload_image(mock_file, folder_name="test_folder")

        assert result == 'https://cloudinary.com/my-image.jpg'


# Test trường hợp lỗi Cloudinary
def test_upload_image_exception():
    mock_file = MagicMock()

    with patch('cloudinary.uploader.upload', side_effect=Exception("Connection Error")):
        result = dao.upload_image(mock_file)

        assert result is None
