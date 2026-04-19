import pytest
from unittest.mock import patch

#trường hợp else
@patch('movieapp.index.render_template')
def test_cinema_route_default(mock_render, test_client, sample_cinemas, test_app):
    # p hàm render trả về một chuỗi ảo để khỏi bị lỗi TemplateNotFound
    mock_render.return_value = "Mocked HTML"
    #Trình duyệt ảo gửi yêu cầu GET từ cinema
    response = test_client.get('/cinemas')

    #Kiểm tra kết quả tải web
    assert response.status_code == 200

    # Kiểm tra xem hệ thống có gọi đúng file giao diện 'cinema.html' không?
    args, kwargs = mock_render.call_args
    assert args[0] == 'cinema.html'

    # danh sách rạp trong tham số cinema
    cinemas_passed_to_template = kwargs['cinemas']
    pages_passed_to_template = kwargs['pages']

    # Đảm bảo danh sách rạp truyền qua giao diện có đủ 3 rạp
    assert len(cinemas_passed_to_template) == 2
    assert pages_passed_to_template==2

    cinema_names = [c.name for c in cinemas_passed_to_template]
    assert "CGV Crescent Mall" in cinema_names
    assert "CGV Tân Phú" in cinema_names


#trường hợp if total=0
@patch('movieapp.dao.load_cinema')
@patch('movieapp.index.render_template')
def test_cinema_total_zero(mock_render, mock_load_cinema, test_client):
    # Ép hàm render trả về một chuỗi ảo để khỏi bị lỗi TemplateNotFound
    mock_render.return_value = "Mocked HTML"
    # 1. Ép hàm dao.load_cinema trả về danh sách rỗng và total = 0
    mock_load_cinema.return_value = ([],0)
    # Trình duyệt ảo gửi yêu cầu GET từ cinema
    response = test_client.get('/cinemas')

    # Kiểm tra kết quả tải web
    assert response.status_code == 200


    # Kiểm tra xem hệ thống có gọi đúng file giao diện 'cinema.html' không?
    args, kwargs = mock_render.call_args
    assert args[0] == 'cinema.html'
    assert kwargs['pages'] == 1




