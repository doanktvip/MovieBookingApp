from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class AdminPage(BasePage):
    URL = 'http://127.0.0.1:5000/admin/'

    BRAND_NAME = (By.CSS_SELECTOR, "a.navbar-brand")

    # Menu cha: Đếm vị trí li trên thanh Navbar
    MENU_CO_SO_VAT_CHAT = (By.CSS_SELECTOR, "ul.navbar-nav > li:nth-child(2) > a")
    MENU_PHIM_LICH_CHIEU = (By.CSS_SELECTOR, "ul.navbar-nav > li:nth-child(3) > a")

    # Menu con: Tìm chính xác theo link href
    SUBMENU_PROVINCE = (By.CSS_SELECTOR, "a[href*='/admin/province']")
    SUBMENU_MOVIE = (By.CSS_SELECTOR, "a[href*='/admin/movie']")
    MENU_USER = (By.CSS_SELECTOR, "a[href*='/admin/user']")

    def open_page(self):
        self.open(self.URL)

    def open_co_so_vat_chat_menu(self):
        self.click(*self.MENU_CO_SO_VAT_CHAT)

    def click_province(self):
        self.js_click(*self.SUBMENU_PROVINCE)

    def open_phim_lich_chieu_menu(self):
        self.js_click(*self.MENU_PHIM_LICH_CHIEU)

    def click_movie(self):
        self.js_click(*self.SUBMENU_MOVIE)

    def click_user_menu(self):
        self.js_click(*self.MENU_USER)
