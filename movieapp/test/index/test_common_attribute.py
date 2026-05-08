import pytest
from unittest.mock import patch
from flask import session


@pytest.fixture(autouse=True)
def mock_render_global(monkeypatch):
    monkeypatch.setattr("movieapp.index.render_template", lambda *args, **kwargs: "Mocked HTML")


def test_common_attribute_logic(test_app):
    with test_app.test_request_context():
        processors = test_app.template_context_processors[None]

        context = {}
        for func in processors:
            res = func()
            if res:
                context.update(res)

        assert 'slugify' in context
        assert context['slugify'] is not None


@patch('movieapp.dao.release_expired_seats')
def test_assign_session_id_logic_flow(mock_release, test_app):
    with test_app.test_request_context():
        session.clear()

        for func in test_app.before_request_funcs[None]:
            if func.__name__ == 'assign_session_id':
                func()

        assert 'user_session_id' in session
        mock_release.assert_called()


@patch('movieapp.dao.release_expired_seats')
def test_assign_session_id_exception_handling(mock_release, test_app):
    mock_release.side_effect = Exception("Forced error for coverage")

    with test_app.test_request_context():
        for func in test_app.before_request_funcs[None]:
            if func.__name__ == 'assign_session_id':
                func()

        mock_release.assert_called()
