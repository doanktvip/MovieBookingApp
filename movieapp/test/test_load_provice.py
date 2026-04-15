from movieapp.test.test_base import sample_provinces,test_session,test_app
from movieapp.dao import load_provinces

def test_load_provinces(sample_provinces):
    result = load_provinces()
    assert len(result) == 3

    result_names = [p.name for p in result]
    assert "Hà Nội" in result_names
    assert "TPHCM" in result_names
    assert "Đà Nẵng" in result_names