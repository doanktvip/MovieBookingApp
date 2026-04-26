from movieapp import dao
from movieapp.models import BookingStatus


def test_get_user_owned_seat_ids_success(sample_full_chain):
    user1 = sample_full_chain["users"]["user1"]
    showtime = sample_full_chain["showtime"]
    ticket = sample_full_chain["ticket"]

    seat_ids = dao.get_user_owned_seat_ids_for_showtime(user1.id, showtime.id)

    assert isinstance(seat_ids, list)
    assert len(seat_ids) == 1
    assert seat_ids[0] == ticket.showtime_seat_id


# Test trường hợp thiếu user_id hoặc showtime_id
def test_get_user_owned_seat_ids_missing_params():
    assert dao.get_user_owned_seat_ids_for_showtime(None, 1) == []
    assert dao.get_user_owned_seat_ids_for_showtime(1, None) == []
    assert dao.get_user_owned_seat_ids_for_showtime(None, None) == []


# Test trường hợp user không có booking nào cho suất chiếu này.
def test_get_user_owned_seat_ids_no_bookings(sample_full_chain):
    user2 = sample_full_chain["users"]["user2"]
    showtime = sample_full_chain["showtime"]

    seat_ids = dao.get_user_owned_seat_ids_for_showtime(user2.id, showtime.id)

    assert seat_ids == []


# Test trường hợp user có booking nhưng trạng thái không phải PAID hay PENDING
def test_get_user_owned_seat_ids_invalid_status(test_session, sample_full_chain):
    user1 = sample_full_chain["users"]["user1"]
    showtime = sample_full_chain["showtime"]
    booking = sample_full_chain["booking"]

    booking.status = BookingStatus.CANCELLED
    test_session.commit()

    seat_ids = dao.get_user_owned_seat_ids_for_showtime(user1.id, showtime.id)

    assert seat_ids == []
