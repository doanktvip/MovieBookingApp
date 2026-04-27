import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.CheckInPage import CheckInPage
from movieapp.test.pages.MovieDetailPage import MovieDetailPage
from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CheckoutPage import CheckoutPage


def create_dummy_ticket_helper(driver):
    movie_page = MovieDetailPage(driver)
    movie_page.open_page()
    time.sleep(1)
    movie_page.click_random_movie()
    time.sleep(1)
    movie_page.click_random_showtime()
    time.sleep(1)

    login_page = LoginPage(driver)
    login_page.login("nguyendoan", "123456")
    time.sleep(1)

    booking_page = BookingPage(driver)
    booking_page.click_random_available_seat()
    booking_page.click_book_button()
    time.sleep(1)

    checkout_page = CheckoutPage(driver)
    checkout_page.select_momo()
    checkout_page.click_pay_button()
    time.sleep(3)

    driver.get("http://127.0.0.1:5000/momo_return?resultCode=0&orderId=DDN-AUTOCHECKIN&message=Success")
    time.sleep(1)

    driver.get("http://127.0.0.1:5000/logout")
    time.sleep(1)


def login_staff_helper(driver):
    login_page = LoginPage(driver)
    login_page.open("http://127.0.0.1:5000/")

    wait = WebDriverWait(driver, 10)

    wait.until(EC.element_to_be_clickable(LoginPage.BUTTON_MODAL_LOGIN))
    login_page.open_login_modal()

    wait.until(EC.element_to_be_clickable(LoginPage.TAB_LOGIN))
    login_page.open_login_tab()
    wait.until(EC.element_to_be_clickable(LoginPage.USERNAME))

    login_page.login("hovandat", "123456")
    time.sleep(2)


def test_access_checkin_page(driver):
    login_staff_helper(driver)
    checkin_page = CheckInPage(driver)
    checkin_page.open_page()
    wait = WebDriverWait(driver, 10)
    title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.card-title")))
    assert "Quản lý Check-in" in title.text


def test_search_booking(driver):
    login_staff_helper(driver)
    checkin_page = CheckInPage(driver)
    checkin_page.open_page()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable(CheckInPage.SEARCH_INPUT))

    search_kw = "nguyendoan"
    checkin_page.search_booking(search_kw)
    time.sleep(2)

    assert f"keyword={search_kw}" in driver.current_url
    search_input = driver.find_element(*CheckInPage.SEARCH_INPUT)
    assert search_input.get_attribute("value") == search_kw


def test_perform_checkin(driver):
    create_dummy_ticket_helper(driver)

    login_staff_helper(driver)
    checkin_page = CheckInPage(driver)
    checkin_page.open_page()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable(CheckInPage.FIRST_CHECKIN_BTN))
    checkin_page.click_first_checkin()
    time.sleep(2)

    status_text = checkin_page.get_first_status_text()
    assert "Đã vào rạp" in status_text

    disabled_btn = driver.find_element(*CheckInPage.FIRST_DISABLED_BTN)
    assert disabled_btn.is_displayed()
    assert "Đã xử lý" in disabled_btn.text
