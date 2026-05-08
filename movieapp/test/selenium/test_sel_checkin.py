from selenium.webdriver.support.ui import WebDriverWait
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.CheckInPage import CheckInPage
from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CheckoutPage import CheckoutPage


def test_access_checkin_page(logged_in_driver):
    test_driver = logged_in_driver("hovandat", "123456")
    checkin_page = CheckInPage(test_driver)
    checkin_page.open_page()
    assert checkin_page.is_title_displayed("Quản lý Check-in")


def test_search_booking(logged_in_driver):
    test_driver = logged_in_driver("hovandat", "123456")
    checkin_page = CheckInPage(test_driver)
    checkin_page.open_page()

    search_kw = "nguyendoan"
    checkin_page.search_booking(search_kw)

    assert f"keyword={search_kw}" in checkin_page.get_current_url()
    assert checkin_page.get_search_input_value() == search_kw


def test_perform_checkin(ready_to_book_driver, logged_in_driver):
    test_driver = ready_to_book_driver

    booking_page = BookingPage(test_driver)
    booking_page.click_random_available_seat()
    booking_page.click_book_button()

    checkout_page = CheckoutPage(test_driver)
    checkout_page.select_momo()
    checkout_page.click_pay_button()

    test_driver.get("http://127.0.0.1:5000/momo_return?resultCode=0&orderId=DDN-AUTOCHECKIN&message=Success")
    test_driver.get("http://127.0.0.1:5000/logout")

    test_driver = logged_in_driver("hovandat", "123456")

    checkin_page = CheckInPage(test_driver)
    checkin_page.open_page()
    checkin_page.click_first_checkin()

    assert "Đã vào rạp" in checkin_page.get_first_status_text()
    assert "Đã xử lý" in checkin_page.get_first_disabled_btn_text()
