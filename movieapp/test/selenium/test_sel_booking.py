import time
from selenium.webdriver.common.by import By
from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CinemaPage import CinemaPage
from movieapp.test.pages.MovieDetailPage import MovieDetailPage
from movieapp.test.pages.LoginPage import LoginPage


def test_booking_from_movie_detail_flow_require_login(driver):
    movie_page = MovieDetailPage(driver)
    movie_page.open_page()
    time.sleep(1)

    movie_page.click_random_movie()
    time.sleep(2)

    movie_page.click_random_showtime()
    time.sleep(1)

    login_page = LoginPage(driver)
    time.sleep(1)

    login_page.login("nguyendoan", "123456")
    time.sleep(2)

    assert "/booking/showtime" in driver.current_url

    seat_area_exists = len(driver.find_elements(By.CSS_SELECTOR, 'input[name="seat_ids"]')) > 0
    assert seat_area_exists is True


def test_booking_from_cinema_flow_require_login(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()
    time.sleep(1)

    cinema_page.click_first_showtime_button()
    time.sleep(1)

    cinema_page.click_first_showtime_in_modal()
    time.sleep(1)

    login_page = LoginPage(driver)

    login_page.login("nguyendoan", "123456")
    time.sleep(2)

    assert "/booking/showtime" in driver.current_url

    seat_area_exists = len(driver.find_elements(By.CSS_SELECTOR, 'input[name="seat_ids"]')) > 0
    assert seat_area_exists is True


def test_select_seat_and_checkout_flow(driver):
    movie_page = MovieDetailPage(driver)
    movie_page.open_page()
    time.sleep(1)

    movie_page.click_random_movie()
    time.sleep(2)

    movie_page.click_random_showtime()
    time.sleep(1)

    login_page = LoginPage(driver)
    time.sleep(1)

    login_page.login("nguyendoan", "123456")
    time.sleep(2)

    booking_page = BookingPage(driver)

    total_price = driver.find_element(By.ID, "total-price")
    assert total_price.text == "0 đ"
    assert booking_page.is_book_button_enabled() is False

    booking_page.click_random_available_seat()

    assert total_price.text != "0 đ"
    assert booking_page.is_book_button_enabled() is True

    booking_page.click_book_button()
    time.sleep(1)

    assert "/checkout" in driver.current_url
