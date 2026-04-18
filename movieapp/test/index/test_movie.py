from unittest.mock import patch


# Kiểm tra logic truyền dữ liệu sang template mặc định
def test_movie_list_default(test_client, sample_movies_data):
    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Fake HTML Content"

        response = test_client.get('/movies')

        assert response.status_code == 200
        call_kwargs = mocked_render.call_args.kwargs

        assert call_kwargs['page'] == 1
        assert call_kwargs['current_kw'] == ''
        assert len(call_kwargs['movies']) > 0


# Kiểm tra lọc phim theo từ khóa
def test_movie_list_search_keyword(test_client, sample_movies_data):
    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Search Result"

        test_client.get('/movies?keyword=Hành+Động')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['current_kw'] == 'Hành Động'
        for m in call_kwargs['movies']:
            assert "Hành Động" in m.name


# Kiểm tra tính năng phân trang với PAGE_SIZE = 2, tổng 3 phim
def test_movie_list_pagination(test_client, sample_movies_data):
    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Page 2 Content"

        test_client.get('/movies?page=2')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['page'] == 2
        assert len(call_kwargs['movies']) == 1


# Kiểm tra khi tham số page không phải là số
def test_movie_list_invalid_page_type(test_client, sample_movies_data):
    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Default Page"

        test_client.get('/movies?page=abc')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['page'] == 1


# Kiểm tra kết hợp cả lọc theo thể loại và từ khóa
def test_movie_list_combined_filters(test_client, sample_movies_data):
    genre_id = sample_movies_data["genres"]["action"].id

    with patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Filtered Content"

        test_client.get(f'/movies?keyword=Hành&genre={genre_id}')

        call_kwargs = mocked_render.call_args.kwargs
        assert call_kwargs['current_kw'] == 'Hành'
        assert str(call_kwargs['current_genre']) == str(genre_id)
