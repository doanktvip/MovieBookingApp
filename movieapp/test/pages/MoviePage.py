from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class MoviePage(BasePage):
    URL = 'http://127.0.0.1:5000/movies'

    SEARCH_INPUT = (By.CSS_SELECTOR, 'input[name="keyword"]')
    SEARCH_BUTTON = (By.CSS_SELECTOR, '#filterForm button[type="submit"]')

    PAGE_2_LINK = (By.CSS_SELECTOR, ".pagination li:nth-child(3) .page-link")

    def open_page(self):
        self.open(self.URL)

    def search_movie(self, text):
        self.typing(*self.SEARCH_INPUT, text)
        self.click(*self.SEARCH_BUTTON)

    def click_genre(self, id):
        genre_label = (By.CSS_SELECTOR, f'label[for="genre-{id}"]')
        self.click(*genre_label)

    def click_page_2(self):
        self.js_click(*self.PAGE_2_LINK)
