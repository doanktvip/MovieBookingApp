import time
from selenium.webdriver.common.by import By
from movieapp.test.pages.MovieDetailPage import MovieDetailPage
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.BookingPage import BookingPage
from movieapp.test.pages.CheckoutPage import CheckoutPage
from movieapp.test.pages.TicketPage import TicketPage


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


def test_checkout_momo_cancel(driver):
    prepare_checkout(driver)

    booking_page = BookingPage(driver)
    booking_page.click_first_available_seat()
    available_seats = driver.find_elements(By.CSS_SELECTOR, "#selected-seats-list > div.bg-danger")
    seat_names = [seat.text for seat in available_seats]
    booking_page.click_book_button()
    time.sleep(1)

    assert "/checkout" in driver.current_url

    checkout_page = CheckoutPage(driver)
    checkout_page.select_momo()
    checkout_page.click_pay_button()

    time.sleep(4)
    assert "/checkout" not in driver.current_url

    momo_cancel_url = "http://127.0.0.1:5000/momo_return?resultCode=1006&orderId=DDN-TEST1234&message=Cancel"
    driver.get(momo_cancel_url)
    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/"
    alert = driver.find_element(By.CLASS_NAME, "alert-danger")
    assert "thất bại" in alert.text.lower() or "hủy" in alert.text.lower()

    ticket_page = TicketPage(driver)
    ticket_page.open_page()
    time.sleep(1)

    target_card = ticket_page.get_booking_card_by_seats(seat_names)
    assert target_card is not None

    status_badge = target_card.find_element(By.CSS_SELECTOR, ".badge")
    assert status_badge.text.strip() == "Đang Chờ"

    clicked = ticket_page.click_pay_again_for_seats(seat_names)
    assert clicked is True

    time.sleep(1)

    assert "/checkout" in driver.current_url


def test_checkout_momo_success(driver):
    prepare_checkout(driver)

    booking_page = BookingPage(driver)
    booking_page.click_first_available_seat()
    available_seats = driver.find_elements(By.CSS_SELECTOR, "#selected-seats-list > div.bg-danger")
    seat_names = [seat.text for seat in available_seats]
    booking_page.click_book_button()
    time.sleep(1)

    assert "/checkout" in driver.current_url

    checkout_page = CheckoutPage(driver)
    checkout_page.select_momo()
    checkout_page.click_pay_button()

    time.sleep(4)
    assert "/checkout" not in driver.current_url

    momo_success_url = "http://127.0.0.1:5000/momo_return?resultCode=0&orderId=DDN-TEST1234&message=Success"
    driver.get(momo_success_url)
    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/"
    alert = driver.find_element(By.CLASS_NAME, "alert-success")
    assert "Thanh toán MoMo thành công!" in alert.text

    ticket_page = TicketPage(driver)
    ticket_page.open_page()
    time.sleep(1)

    target_card = ticket_page.get_booking_card_by_seats(seat_names)
    assert target_card is not None

    status_badge = target_card.find_element(By.CSS_SELECTOR, ".badge")
    assert status_badge.text.strip() == "Đã Thanh Toán"

    modal_id = ticket_page.click_cancel_for_seats(seat_names)
    assert modal_id is not None

    time.sleep(1)

    confirm_btn_selector = f"{modal_id} button[type='submit'].btn-danger"
    confirm_btn = driver.find_element(By.CSS_SELECTOR, confirm_btn_selector)
    confirm_btn.click()

    time.sleep(2)

    result_alert = driver.find_element(By.CSS_SELECTOR, ".alert-success, .alert-danger")
    alert_msg = result_alert.text

    assert "Đã hủy vé thành công!" in alert_msg or "Chỉ được hủy vé trước giờ chiếu ít nhất 2 tiếng!" in alert_msg

def test_ticket_page_edge_cases_and_exceptions(driver):
    prepare_checkout(driver)

    ticket_page = TicketPage(driver)
    ticket_page.open_page()
    time.sleep(1)

    fake_seats = ["Ghế Ảo 999"]

    assert ticket_page.click_pay_again_for_seats(fake_seats) is False

    assert ticket_page.click_cancel_for_seats(fake_seats) is None

    driver.execute_script("""
        let badCard = document.createElement('div');
        badCard.className = 'col-12 mb-4';
        badCard.innerHTML = '<p>Ghế: Thẻ bị thiếu cấu trúc strong</p>';
        document.body.appendChild(badCard);
    """)

    assert ticket_page.get_booking_card_by_seats(fake_seats) is None
