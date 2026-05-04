from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CheckoutPage import CheckoutPage
from movieapp.test.pages.HomePage import HomePage
from movieapp.test.pages.TicketPage import TicketPage


def prepare_checkout(driver):
    booking_page = BookingPage(driver)
    booking_page.click_random_available_seat()
    booking_page.click_book_button()

    checkout_page = CheckoutPage(driver)
    assert checkout_page.is_on_page()

    checkout_page.select_momo()
    checkout_page.click_pay_button()


def test_checkout_momo_cancel_flow(ready_to_book_driver):
    test_driver = ready_to_book_driver
    prepare_checkout(test_driver)
    momo_cancel_url = "http://127.0.0.1:5000/momo_return?resultCode=1006&orderId=DDN-TEST1234&message=Cancel"
    test_driver.get(momo_cancel_url)

    home_page = HomePage(test_driver)
    assert home_page.get_current_url() == "http://127.0.0.1:5000/"

    ticket_page = TicketPage(test_driver)
    alert = ticket_page.get_alert_message()
    assert "thất bại" in alert.lower() or "hủy" in alert.lower()


def test_checkout_momo_success_flow(ready_to_book_driver):
    test_driver = ready_to_book_driver
    prepare_checkout(test_driver)
    momo_success_url = "http://127.0.0.1:5000/momo_return?resultCode=0&orderId=DDN-TEST1234&message=Success"
    test_driver.get(momo_success_url)

    home_page = HomePage(test_driver)
    assert home_page.get_current_url() == "http://127.0.0.1:5000/"

    ticket_page = TicketPage(test_driver)
    alert = ticket_page.get_alert_message()
    assert "thành công" in alert.lower()
