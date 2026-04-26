import time
from selenium.webdriver.common.by import By
from movieapp.test.pages.MovieDetailPage import MovieDetailPage
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CheckoutPage import CheckoutPage


def prepare_checkout(driver):
    movie_page = MovieDetailPage(driver)
    movie_page.open_page()
    time.sleep(1)
    movie_page.click_first_movie()
    time.sleep(1)
    movie_page.click_first_showtime()
    time.sleep(1)

    login_page = LoginPage(driver)
    login_page.login("nguyendoan", "123456")
    time.sleep(1)

    booking_page = BookingPage(driver)
    booking_page.click_first_available_seat()
    booking_page.click_book_button()
    time.sleep(1)

    assert "/checkout" in driver.current_url

    checkout_page = CheckoutPage(driver)
    checkout_page.select_momo()
    checkout_page.click_pay_button()

    time.sleep(2)
    assert "/checkout" not in driver.current_url


# ĐẶT VÉ NHƯNG HỦY THANH TOÁN TẠI CỔNG MOMO
def test_checkout_momo_cancel_flow(driver):
    prepare_checkout(driver)
    momo_cancel_url = "http://127.0.0.1:5000/momo_return?resultCode=1006&orderId=DDN-TEST1234&message=Cancel"
    driver.get(momo_cancel_url)
    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/"
    alert = driver.find_element(By.CLASS_NAME, "alert-danger")
    assert "thất bại" in alert.text or "hủy" in alert.text


# ĐẶT VÉ VÀ THANH TOÁN MOMO THÀNH CÔNG
def test_checkout_momo_success_flow(driver):
    prepare_checkout(driver)
    momo_success_url = "http://127.0.0.1:5000/momo_return?resultCode=0&orderId=DDN-TEST1234&message=Success"
    driver.get(momo_success_url)
    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/"
    alert = driver.find_element(By.CLASS_NAME, "alert-success")
    assert "Thanh toán MoMo thành công!" in alert.text
