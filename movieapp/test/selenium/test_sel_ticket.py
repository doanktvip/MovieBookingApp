from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CheckoutPage import CheckoutPage
from movieapp.test.pages.TicketPage import TicketPage
from movieapp.test.pages.HomePage import HomePage


def test_checkout_momo_cancel(ready_to_book_driver):
    test_driver = ready_to_book_driver
    booking_page = BookingPage(test_driver)
    booking_page.click_random_available_seat()
    seat_names = booking_page.get_selected_seat_names()
    booking_page.click_book_button()

    checkout_page = CheckoutPage(test_driver)
    assert checkout_page.is_on_page()
    checkout_page.select_momo()
    checkout_page.click_pay_button()

    test_driver.get("http://127.0.0.1:5000/momo_return?resultCode=1006&orderId=DDN-TEST1234&message=Cancel")

    home_page = HomePage(test_driver)
    assert home_page.get_current_url() == "http://127.0.0.1:5000/"

    ticket_page = TicketPage(test_driver)
    alert = ticket_page.get_alert_message()
    assert "thất bại" in alert.lower() or "hủy" in alert.lower()

    ticket_page.open_page()
    assert ticket_page.get_status_badge_text(seat_names) == "Đang Chờ"
    assert ticket_page.click_pay_again_for_seats(seat_names) is True
    assert checkout_page.is_on_page()


def test_checkout_momo_success(ready_to_book_driver):
    test_driver = ready_to_book_driver
    booking_page = BookingPage(test_driver)
    booking_page.click_random_available_seat()
    seat_names = booking_page.get_selected_seat_names()
    booking_page.click_book_button()

    checkout_page = CheckoutPage(test_driver)
    assert checkout_page.is_on_page()
    checkout_page.select_momo()
    checkout_page.click_pay_button()

    test_driver.get("http://127.0.0.1:5000/momo_return?resultCode=0&orderId=DDN-TEST1234&message=Success")

    ticket_page = TicketPage(test_driver)
    assert "thành công" in ticket_page.get_alert_message().lower()

    ticket_page.open_page()
    assert ticket_page.get_status_badge_text(seat_names) == "Đã Thanh Toán"

    modal_id = ticket_page.click_cancel_for_seats(seat_names)
    assert modal_id is not None
    ticket_page.confirm_cancel(modal_id)

    alert = ticket_page.get_alert_message()
    assert "thành công" in alert.lower() or "ít nhất 2 tiếng" in alert.lower()


def test_ticket_page_edge_cases_and_exceptions(ready_to_book_driver):
    test_driver = ready_to_book_driver
    ticket_page = TicketPage(test_driver)
    ticket_page.open_page()

    fake_seats = ["Ghế Ảo 999"]
    assert ticket_page.click_pay_again_for_seats(fake_seats) is False
    assert ticket_page.click_cancel_for_seats(fake_seats) is None

    test_driver.execute_script("""
        let badCard = document.createElement('div');
        badCard.className = 'col-12 mb-4';
        badCard.innerHTML = '<p>Ghế: Thẻ bị thiếu cấu trúc strong</p>';
        document.body.appendChild(badCard);
    """)
    assert ticket_page.get_booking_card_by_seats(fake_seats) is None
