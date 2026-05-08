from selenium.webdriver.common.by import By

from movieapp.test.pages.BasePage import BasePage


class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'

    HERO_ACTIVE_TITLE = (By.CSS_SELECTOR, '#heroCarousel .carousel-item.active .movie-title')

    HERO_NEXT_BTN = (By.CSS_SELECTOR, '#heroCarousel .carousel-control-next')

    KHAM_PHA_NGAY_BTN = (By.CSS_SELECTOR, "a.btn-danger.mt-5")

    def open_page(self):
        self.open(self.URL)

    def get_active_hero_movie_title(self):
        return self.get_text(*self.HERO_ACTIVE_TITLE)

    def click_next_hero_slide(self):
        self.click(*self.HERO_NEXT_BTN)

    def wait_for_slide_change(self, previous_title):
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.driver, 5).until(
            lambda driver: self.get_active_hero_movie_title() != previous_title
        )

    def click_kham_pha_ngay(self):
        self.js_click(*self.KHAM_PHA_NGAY_BTN)
