from movieapp.dao import load_bookings_for_checkin
from movieapp.test.conftest import sample_full_chain


# ==========================================
# KIỂM THỬ LOAD BOOKING CHECK-IN (READ)
# ==========================================

def test_load_bookings_all(sample_full_chain):
    actual_bookings, total_page = load_bookings_for_checkin()

    assert len(actual_bookings) >= 1
    assert actual_bookings[0].user.username == "new_user1"


def test_load_bookings_kw_match(sample_full_chain):

    actual_bookings, total_page = load_bookings_for_checkin(kw='new_user')

    assert len(actual_bookings) == 1
    assert "new_user" in actual_bookings[0].user.username.lower()


def test_load_bookings_kw_not_found(sample_full_chain):
    actual_bookings, total_page = load_bookings_for_checkin(kw='nonexistent')
    assert len(actual_bookings) == 0


def test_load_bookings_pagination(sample_full_chain):
    actual_bookings, total_page = load_bookings_for_checkin(page=1)

    assert len(actual_bookings) > 0
    assert total_page >= 1


def test_load_bookings_pagination_with_kw(sample_full_chain):
    actual_bookings, total_page = load_bookings_for_checkin(kw='user1', page=1)

    assert len(actual_bookings) == 1
    assert total_page == 1
    assert actual_bookings[0].user.username == "new_user1"
