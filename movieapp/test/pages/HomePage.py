from selenium.webdriver.common.by import By

from movieapp.test.pages.BasePage import BasePage


class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'

    HERO_ACTIVE_TITLE = (By.CSS_SELECTOR, '#heroCarousel .carousel-item.active .movie-title')

    HERO_NEXT_BTN = (By.CSS_SELECTOR, '#heroCarousel .carousel-control-next')

    KHAM_PHA_NGAY_BTN = (By.CSS_SELECTOR, "a.btn-danger.mt-5")

    def open_page(self):
        self.open(self.URL)

    # Lấy tên bộ phim đang hiển thị trên slide to nhất
    def get_active_hero_movie_title(self):
        return self.find(*self.HERO_ACTIVE_TITLE).text

    # Bấm nút mũi tên phải trên slide
    def click_next_hero_slide(self):
        self.click(*self.HERO_NEXT_BTN)

    def click_kham_pha_ngay(self):
        self.js_click(*self.KHAM_PHA_NGAY_BTN)
