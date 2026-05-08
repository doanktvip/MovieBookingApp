from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.MoviePage import MoviePage


def test_search_movie(driver):
    movie_page = MoviePage(driver)
    movie_page.open_page()

    keyword = "Avatar"
    movie_page.search_movie(keyword)
    WebDriverWait(driver, 10).until(EC.url_contains(keyword))
    titles = movie_page.get_movie_titles()
    for name in titles:
        assert keyword.lower() in name.lower()


def test_filter_genre(driver):
    movie_page = MoviePage(driver)
    movie_page.open_page()

    genre_id = 1
    movie_page.click_genre(genre_id)

    assert f"genre={genre_id}" in movie_page.get_current_url()


def test_pagination(driver):
    movie_page = MoviePage(driver)
    movie_page.open_page()

    movie_page.click_page_2()

    assert "page=2" in movie_page.get_current_url()
