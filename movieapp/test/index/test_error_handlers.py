from unittest.mock import patch

from flask import current_app


# Kích hoạt errorhandler(404)
def test_error_404_redirect(test_client):
    response = test_client.get('/duong-dan-khong-ton-tai-123')

    assert response.status_code == 404


# Kích hoạt errorhandler(405)
def test_error_405_redirect(test_client):
    response = test_client.post('/')

    assert response.status_code == 405


# Kiểm tra redirect 404 khi không ở chế độ testing
def test_handle_404_redirect_non_testing(test_client):
    with patch.dict(current_app.config, {"TESTING": False}):
        response = test_client.get('/duong-dan-khong-ton-tai-404')
        assert response.status_code == 302
        assert response.location == "/"


# Kiểm tra redirect 405 khi không ở chế độ testing
def test_handle_405_redirect_non_testing(test_client):
    with patch.dict(current_app.config, {"TESTING": False}):
        response = test_client.post('/')
        assert response.status_code == 302
        assert response.location == "/"
