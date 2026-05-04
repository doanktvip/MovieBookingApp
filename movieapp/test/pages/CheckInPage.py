from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class CheckInPage(BasePage):
    URL = 'http://127.0.0.1:5000/check_in'

    SEARCH_INPUT = (By.NAME, "keyword")
    SEARCH_BTN = (By.CSS_SELECTOR, "form[action*='check_in'] button[type='submit']")

    FIRST_ROW = (By.CSS_SELECTOR, "tbody tr:first-child")
    FIRST_CHECKIN_BTN = (By.CSS_SELECTOR, "tbody tr:first-child button[name='submit_checkin']")
    FIRST_STATUS_TEXT = (By.CSS_SELECTOR, "tbody tr:first-child td:nth-child(6) span")
    FIRST_DISABLED_BTN = (By.CSS_SELECTOR, "tbody tr:first-child td:nth-child(7) button[disabled]")

    def open_page(self):
        self.open(self.URL)

    def search_booking(self, keyword):
        self.js_typing(*self.SEARCH_INPUT, keyword)
        self.js_click(*self.SEARCH_BTN)

    def click_first_checkin(self):
        self.click(*self.FIRST_CHECKIN_BTN)

    def get_first_status_text(self):
        return self.get_text(*self.FIRST_STATUS_TEXT)

    def get_first_disabled_btn_text(self):
        if self.is_displayed(*self.FIRST_DISABLED_BTN):
            return self.get_text(*self.FIRST_DISABLED_BTN)

    def get_search_input_value(self):
        return self.find(*self.SEARCH_INPUT).get_attribute("value")

    def is_title_displayed(self, expected_title):
        title = self.find(By.CSS_SELECTOR, "h1.card-title")
        return expected_title in title.text
