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

def test_pagination(sample_cinemas):
    page1_cinema,total1=load_cinema(page=1)
    assert len(page1_cinema) > 0
    assert total1 == len(sample_cinemas)


def test_pagination_kw(sample_cinemas):
    page_2,total2=load_cinema(page=1,keyword="CGV")
    assert len(page_2)>0
    assert page_2[0].name=="CGV Tân Phú"

def test_pagination_kw_province(sample_cinemas):
    p1_cinemas, total1 = load_cinema(keyword="CGV", province_id=2, page=1)
    assert len(p1_cinemas)==1
    assert total1==1
    assert p1_cinemas[0].name=="CGV Yên Lãng"

    p_empty, total2 = load_cinema(keyword="CGV", province_id=2, page=100)
    assert len(p_empty) == 0
    assert total2 == 1

