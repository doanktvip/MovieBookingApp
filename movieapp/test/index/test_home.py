from unittest.mock import patch, MagicMock


# Kiểm tra trang chủ render đúng template và dữ liệu
def test_index_route_success(test_client):
    mock_movies = [MagicMock(id=1, name="Movie 1"), MagicMock(id=2, name="Movie 2")]
    mock_genres = [MagicMock(id=1, name="Action"), MagicMock(id=2, name="Comedy")]
    mock_tien_ich = [{"id": 1, "name": "Wifi"}, {"id": 2, "name": "Parking"}]

    with patch('movieapp.dao.load_movies') as mocked_movies, \
            patch('movieapp.dao.load_genres') as mocked_genres, \
            patch('movieapp.dao.load_tien_ich') as mocked_tien_ich_func, \
            patch('movieapp.index.render_template') as mocked_render:
        mocked_movies.return_value = mock_movies
        mocked_genres.return_value = mock_genres
        mocked_tien_ich_func.return_value = mock_tien_ich
        mocked_render.return_value = "Home Page Content"

        response = test_client.get('/')

        assert response.status_code == 200

        mocked_movies.assert_called_once()
        mocked_genres.assert_called_once()
        mocked_tien_ich_func.assert_called_once()

        mocked_render.assert_called_once_with(
            'index.html',
            movies=mock_movies,
            genres=mock_genres,
            tien_ich=mock_tien_ich
        )


# Kiểm tra trang chủ vẫn hoạt động tốt khi database rỗng
def test_index_route_empty_data(test_client):
    with patch('movieapp.dao.load_movies', return_value=[]), \
            patch('movieapp.dao.load_genres', return_value=[]), \
            patch('movieapp.dao.load_tien_ich', return_value=[]), \
            patch('movieapp.index.render_template') as mocked_render:
        mocked_render.return_value = "Empty Home"
        response = test_client.get('/')

        assert response.status_code == 200
        _, kwargs = mocked_render.call_args
        assert kwargs['movies'] == []
        assert kwargs['genres'] == []
