from movieapp.dao import load_provinces
from movieapp.test.conftest import test_app, sample_basic_setup


def test_load_provinces_success(sample_basic_setup):
    result = load_provinces()
    assert len(result) == 2

    result_names = [p.name for p in result]

    assert "TP.HCM" in result_names
    assert "Hà Nội" in result_names


def test_load_provinces_empty(test_app):
    result = load_provinces()
    assert len(result) == 0
