import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.CinemaPage import CinemaPage


def test_search_cinema(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()
    time.sleep(1)

    keyword = "CGV"
    cinema_page.search_cinema(keyword)
    time.sleep(1)

    titles = driver.find_elements(By.CSS_SELECTOR, '#cinema-container h3.fw-bold')
    for title in titles:
        assert keyword.lower() in title.text.lower()


def test_filter_cinema_by_province(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()
    time.sleep(1)

    province_id = "1"
    cinema_page.select_province_by_value(province_id)
    time.sleep(1)

    assert f"province_id={province_id}" in driver.current_url


def test_open_cinema_showtime_modal(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()
    time.sleep(1)

    cinema_page.click_first_showtime_button()

    wait = WebDriverWait(driver, 5)
    active_modal = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.modal.show')))
    assert active_modal.is_displayed() is True
