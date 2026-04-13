from movieapp.dao import load_cinema
from movieapp.test.test_base import sample_cinemas,test_session,test_app


def test_all(sample_cinemas):
    actual_cinemas,total=load_cinema()

    assert len(actual_cinemas)==len(sample_cinemas)

def test_kw(sample_cinemas):
    actual_cinemas,total=load_cinema(keyword="CGV")
    assert len(actual_cinemas)==3
    assert all ('CGV' in c.name for c in actual_cinemas)

def test_zero(sample_cinemas):
    actual_cinemas,total=load_cinema(keyword="addssfaf")
    assert len(actual_cinemas)==0

def test_province_cinema(sample_cinemas):
    actual_cinemas,total=load_cinema(province_id=1)
    assert len(actual_cinemas)==2
    assert all(c.province_id ==1 for c in actual_cinemas)

def test_kw_province_cinema(sample_cinemas):
    actual_cinemas,total=load_cinema(keyword="CGV",province_id=2)
    assert len(actual_cinemas)==1
    assert actual_cinemas[0].name=="CGV Yên Lãng"
