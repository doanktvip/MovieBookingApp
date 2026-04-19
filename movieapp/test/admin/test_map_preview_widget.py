from unittest.mock import MagicMock

from movieapp.admin import MapPreviewWidget


def test_map_preview_widget():
    # Tạo widget
    widget = MapPreviewWidget()

    # Tạo field giả lập của WTForms
    mock_field = MagicMock()
    mock_field.id = 'map_url'
    mock_field.name = 'map_url'
    mock_field.data = 'http://map.com'

    # Render ra HTML
    html = widget(mock_field)

    # Kiểm tra xem mã HTML sinh ra có chứa dữ liệu và tên hàm JS không
    assert 'http://map.com' in html
    assert 'previewMap()' in html
