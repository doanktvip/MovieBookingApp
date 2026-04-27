import random

from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class MovieDetailPage(BasePage):
    URL = 'http://127.0.0.1:5000/movies'

    SHOWTIME_LINKS = (By.CSS_SELECTOR, '#showtime-container a')

    ALL_MOVIE_LINKS = (By.CSS_SELECTOR, '#movie-container > div.row.g-4 > div > a')
    selected_index = 0

    def open_page(self):
        self.open(self.URL)

    def get_movie_title_random(self):
        elements = self.finds(*self.ALL_MOVIE_LINKS)
        self.selected_index = random.randint(0, len(elements) - 1)
        full_card_text = elements[self.selected_index].text.strip()
        title_only = full_card_text.split('\n')[1]
        return title_only

    def click_random_movie(self):
        elements = self.finds(*self.ALL_MOVIE_LINKS)
        self.driver.execute_script("arguments[0].click();", elements[self.selected_index])

    def click_random_showtime(self):
        self.js_clicks(*self.SHOWTIME_LINKS)
