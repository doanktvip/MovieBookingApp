from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class BookingPage(BasePage):
    AVAILABLE_SEAT_LABELS = (By.CSS_SELECTOR, "input.seat-check:not(:checked) + label.seat-box")
    BOOK_BUTTON = (By.ID, "btn-book-seats")

    def click_random_available_seat(self):
        self.js_clicks(*self.AVAILABLE_SEAT_LABELS)

    def is_book_button_enabled(self):
        btn = self.find(*self.BOOK_BUTTON)
        return btn.get_attribute("disabled") is None

    def click_book_button(self):
        self.js_click(*self.BOOK_BUTTON)
