from movieapp.dao import load_bookings_for_checkin
from movieapp.test.test_base import test_session, test_app, sample_rooms, sample_users, sample_movies,sample_bookings_for_checkin,sample_cinemas

def test_all(sample_bookings_for_checkin):
    actual_bookings,total_page=load_bookings_for_checkin()
    assert len(actual_bookings)==len(sample_bookings_for_checkin)

def test_kw(sample_bookings_for_checkin):
    actual_bookings,total_page=load_bookings_for_checkin(kw='dat')
    assert len(actual_bookings)==2
    assert all('dat' in b.user.username.lower() for b in actual_bookings)

def test_zero(sample_bookings_for_checkin):
    actual_bookings,total_page=load_bookings_for_checkin(kw='aaaaa')
    assert len(actual_bookings)==0

def test_pagination(sample_bookings_for_checkin):
    actual_bookings,total_page=load_bookings_for_checkin(page=1)
    assert len(actual_bookings)>0
    assert total_page == 1

def test_pagination_kw(sample_bookings_for_checkin):
    actual_bookings,total_page=load_bookings_for_checkin(kw='dat',page=1)
    assert len(actual_bookings)>0
    assert all('dat' in b.user.username.lower() for b in actual_bookings)