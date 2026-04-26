import time
from selenium.webdriver.common.by import By
from movieapp.test.pages.MovieDetailPage import MovieDetailPage


def test_view_first_movie_detail_and_showtimes(driver):
    movie_detail_page = MovieDetailPage(driver)
    movie_detail_page.open_page()
    time.sleep(1)
    title_movie_first = driver.find_element(By.CSS_SELECTOR, '#movie-container div:nth-child(1) h5').text
    time.sleep(1)
    movie_detail_page.click_first_movie()
    time.sleep(1)
    detail_page = MovieDetailPage(driver)

    assert "/movies/" in driver.current_url

    movie_title = detail_page.get_movie_title()
    assert movie_title == title_movie_first
    # Kiểm tra xem tab Lịch chiếu có đang được chọn (active) hay không
    showtime_tab = driver.find_element(By.ID, 'pills-showtime-tab')
    assert "active" in showtime_tab.get_attribute("class")

    # Kiểm tra xem khu vực chứa lịch chiếu có hiển thị trên màn hình không
    showtime_container = driver.find_element(By.ID, 'showtime-container')
    assert showtime_container.is_displayed()
