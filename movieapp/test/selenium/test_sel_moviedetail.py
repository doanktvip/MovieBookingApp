import time
from selenium.webdriver.common.by import By
from movieapp.test.pages.MovieDetailPage import MovieDetailPage


def test_view_random_movie_detail_and_showtimes(driver):
    movie_detail_page = MovieDetailPage(driver)
    movie_detail_page.open_page()
    movie_title_random = movie_detail_page.get_movie_title_random()
    time.sleep(1)
    movie_detail_page.click_random_movie()
    time.sleep(1)

    assert "/movies/" in driver.current_url
    movie_title = driver.find_element(By.CSS_SELECTOR, 'h1.movie-title').text
    assert movie_title == movie_title_random
    showtime_tab = driver.find_element(By.ID, 'pills-showtime-tab')
    assert "active" in showtime_tab.get_attribute("class")

    showtime_container = driver.find_element(By.ID, 'showtime-container')
    assert showtime_container.is_displayed()
