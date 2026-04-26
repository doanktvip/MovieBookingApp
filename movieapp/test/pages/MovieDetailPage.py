from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class MovieDetailPage(BasePage):
    URL = 'http://127.0.0.1:5000/movies'

    MOVIE_TITLE = (By.CSS_SELECTOR, 'h1.movie-title')
    MOVIE_LINKS = (By.CSS_SELECTOR, '#movie-container > div.row.g-4 > div:nth-child(1) > a')

    FIRST_SHOWTIME_LINK = (By.CSS_SELECTOR, '#showtime-container div:nth-child(1) a:nth-child(1)')

    def open_page(self):
        self.open(self.URL)

    def get_movie_title(self):
        return self.find(*self.MOVIE_TITLE).text

    def click_first_movie(self):
        self.click(*self.MOVIE_LINKS)

    def click_first_showtime(self):
        self.js_click(*self.FIRST_SHOWTIME_LINK)
