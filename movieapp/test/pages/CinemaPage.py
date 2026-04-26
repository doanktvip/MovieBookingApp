from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.BasePage import BasePage


class CinemaPage(BasePage):
    URL = 'http://127.0.0.1:5000/cinemas'

    SEARCH_INPUT = (By.CSS_SELECTOR, 'input[name="keyword_cinema"]')
    SEARCH_BUTTON = (By.CSS_SELECTOR, '#cinemaFilterForm button[type="submit"]')
    PROVINCE_SELECT = (By.CSS_SELECTOR, 'select > option')
    SHOWTIME_BUTTONS = (By.CSS_SELECTOR, 'div:nth-child(1) button[data-bs-target^="#exampleModalCenter"]')

    FIRST_SHOWTIME_LINK_IN_MODAL = (By.CSS_SELECTOR, 'div[id^="showtime-content-"] > div:nth-child(1) a:nth-child(1)')

    def open_page(self):
        self.open(self.URL)

    def search_cinema(self, text):
        self.typing(*self.SEARCH_INPUT, text)
        self.click(*self.SEARCH_BUTTON)

    def select_province_by_value(self, province):
        province_str = str(province)
        select_elements = self.finds(*self.PROVINCE_SELECT)
        for select_element in select_elements:
            element_value = select_element.get_attribute('value')
            if element_value == province_str:
                select_element.click()
                break

    def click_first_showtime_button(self):
        self.click(*self.SHOWTIME_BUTTONS)

    def click_first_showtime_in_modal(self):
        self.js_click(*self.FIRST_SHOWTIME_LINK_IN_MODAL)
