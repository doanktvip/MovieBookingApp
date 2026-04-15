import pytest
from movieapp.dao import load_bookings_for_checkin
from movieapp.test.test_base import test_session, test_app, sample_full_chain, sample_users, sample_showtimes_complex, \
    sample_movies_data, sample_cinemas, sample_basic_setup


# ==========================================
# KIỂM THỬ LOAD BOOKING CHECK-IN (READ)
# ==========================================

def test_load_bookings_all(sample_full_chain):
    """Kiểm tra tải toàn bộ danh sách đơn hàng để check-in"""
    # Fixture sample_full_chain tạo sẵn 1 booking
    actual_bookings, total_page = load_bookings_for_checkin()

    assert len(actual_bookings) >= 1
    # Kiểm tra object trả về có đúng là Booking không
    assert actual_bookings[0].user.username == "new_user1"


def test_load_bookings_kw_match(sample_full_chain):
    """Kiểm tra tìm kiếm theo từ khóa (Username)"""
    # Username trong fixture là 'new_user1'
    actual_bookings, total_page = load_bookings_for_checkin(kw='new_user')

    assert len(actual_bookings) == 1
    assert "new_user" in actual_bookings[0].user.username.lower()


def test_load_bookings_kw_not_found(sample_full_chain):
    """Kiểm tra tìm kiếm với từ khóa không tồn tại"""
    actual_bookings, total_page = load_bookings_for_checkin(kw='nonexistent')

    assert len(actual_bookings) == 0


def test_load_bookings_pagination(sample_full_chain):
    """Kiểm tra phân trang"""
    # app.config['PAGE_SIZE'] = 2
    actual_bookings, total_page = load_bookings_for_checkin(page=1)

    assert len(actual_bookings) > 0
    assert total_page >= 1


def test_load_bookings_pagination_with_kw(sample_full_chain):
    """Kiểm tra kết hợp phân trang và từ khóa"""
    actual_bookings, total_page = load_bookings_for_checkin(kw='user1', page=1)

    assert len(actual_bookings) == 1
    assert total_page == 1
    assert actual_bookings[0].user.username == "new_user1"
