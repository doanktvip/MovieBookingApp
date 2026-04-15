from movieapp.test.test_base import sample_genres,test_session,test_app
from movieapp.dao import load_genres

def test_load_genre(sample_genres):
    result=load_genres()
    assert len(result)==3

    result_names = [g.name for g in result]
    assert "Hành động" in result_names
    assert "Kinh dị" in result_names
    assert "Phiêu lưu" in result_names