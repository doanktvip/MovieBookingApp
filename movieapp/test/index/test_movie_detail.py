from unittest.mock import patch
from datetime import datetime, timedelta


# Kiểm tra hiển thị chi tiết phim với ID hợp lệ và dữ liệu mặc định.
def test_movie_detail_success(test_client, sample_movies_data):
    movie_id = sample_movies_data["movies"]["hot"].id

    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Movie Detail Content"

        response = test_client.get(f'/movies/{movie_id}')

        assert response.status_code == 200
        call_kwargs = mocked_render.call_args.kwargs

        # Kiểm tra thông tin phim
        assert call_kwargs['movie'].id == movie_id
        assert len(call_kwargs['sorted_dates']) == 7
        assert call_kwargs['page'] == 1
        assert call_kwargs['current_format'] == ''


# Kiểm tra khi áp dụng các bộ lọc: ngày, định dạng và ngôn ngữ.
def test_movie_detail_with_filters(test_client, sample_movies_data):
    movie_id = sample_movies_data["movies"]["hot"].id
    target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Filtered Detail"

        url = f'/movies/{movie_id}?date={target_date}&format=2D&language=SUBTITLE&page=1'
        test_client.get(url)

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['current_date'] == target_date
        assert call_kwargs['current_format'] == '2D'
        assert call_kwargs['current_lang'] == 'SUBTITLE'


# Kiểm tra logic phân trang khi xem danh sách rạp
def test_movie_detail_pagination(test_client, sample_movies_data):
    movie_id = sample_movies_data["movies"]["hot"].id

    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Page 2"

        # Giả lập chuyển sang trang 2 của danh sách rạp
        test_client.get(f'/movies/{movie_id}?page=2')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['page'] == 2
        # Kiểm tra dải trang được tính toán từ dao.get_page_range
        assert 'page_range' in call_kwargs


# Kiểm tra trường hợp truyền ngôn ngữ không tồn tại trong Enum TranslationType.
def test_movie_detail_invalid_language_enum(test_client, sample_movies_data):
    movie_id = sample_movies_data["movies"]["hot"].id

    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Error Case"

        test_client.get(f'/movies/{movie_id}?language=INVALID_LANG')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['cinema_showtimes'] == {}
        assert call_kwargs['total_pages'] == 0


# Kiểm tra khi xem một ID phim không tồn tại trong DB.
def test_movie_detail_not_found_movie(test_client):
    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "No Movie"

        test_client.get('/movies/99999')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['movie'] is None
