from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CinemaPage import CinemaPage
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.CheckoutPage import CheckoutPage
from movieapp.test.pages.MovieDetailPage import MovieDetailPage


def test_booking_from_movie_detail_flow_require_login(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")
    movie_page = MovieDetailPage(test_driver)

    movie_page.select_random_valid_movie_and_showtime()

    WebDriverWait(test_driver, 10).until(EC.url_contains("/booking/showtime"))

    booking_page = BookingPage(test_driver)
    assert booking_page.has_seat_area()


def test_booking_from_cinema_flow_require_login(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")

    cinema_page = CinemaPage(test_driver)
    cinema_page.open_page()
    cinema_page.click_first_showtime_button()
    cinema_page.click_first_showtime_in_modal()

    WebDriverWait(test_driver, 10).until(EC.url_contains("/booking/showtime"))

    booking_page = BookingPage(test_driver)
    assert booking_page.has_seat_area()


def test_select_seat_and_checkout_flow(ready_to_book_driver):
    test_driver = ready_to_book_driver
    booking_page = BookingPage(test_driver)

    assert booking_page.get_total_price() == "0 đ"
    assert booking_page.is_book_button_enabled() is False

    booking_page.click_random_available_seat()

    assert booking_page.get_total_price() != "0 đ"
    assert booking_page.is_book_button_enabled() is True

    booking_page.click_book_button()

    checkout_page = CheckoutPage(test_driver)
    assert checkout_page.is_on_page()
