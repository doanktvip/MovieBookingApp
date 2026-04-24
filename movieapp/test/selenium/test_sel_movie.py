import time
import pytest
from selenium.webdriver.common.by import By
from movieapp.test.pages.MoviePage import MoviePage


def test_search_movie(driver):
    movie_page = MoviePage(driver)
    movie_page.open_page()
    time.sleep(1)
    keyword = "Avatar"
    movie_page.search_movie(keyword)

    time.sleep(1)
    titles = driver.find_elements(By.CSS_SELECTOR, '#movie-container div.row h5')

    for name in titles:
        assert keyword.lower() in name.text.lower()


def test_filter_genre(driver):
    movie_page = MoviePage(driver)
    movie_page.open_page()
    genre_id = 1
    movie_page.click_genre(genre_id)
    time.sleep(1)

    assert f"genre={genre_id}" in driver.current_url


def test_pagination(driver):
    movie_page = MoviePage(driver)
    movie_page.open_page()

    movie_page.click_page_2()
    time.sleep(1)
    assert "page=2" in driver.current_url
