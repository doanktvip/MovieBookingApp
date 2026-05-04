from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage

class BookingPage(BasePage):
    AVAILABLE_SEAT_LABELS = (By.CSS_SELECTOR, "input.seat-check:not(:checked) + label.seat-box")
    BOOK_BUTTON = (By.ID, "btn-book-seats")
    TOTAL_PRICE = (By.ID, "total-price")
    SELECTED_SEATS = (By.CSS_SELECTOR, "#selected-seats-list > div.bg-danger")
    SEAT_AREA_INPUTS = (By.CSS_SELECTOR, 'input[name="seat_ids"]')

    def click_random_available_seat(self):
        self.js_clicks(*self.AVAILABLE_SEAT_LABELS)

    def is_book_button_enabled(self):
        btn = self.find(*self.BOOK_BUTTON)
        return btn.get_attribute("disabled") is None

    def click_book_button(self):
        self.js_click(*self.BOOK_BUTTON)

    def get_total_price(self):
        return self.get_text(*self.TOTAL_PRICE)

    def get_selected_seat_names(self):
        elements = self.driver.find_elements(*self.SELECTED_SEATS)
        return [e.text for e in elements]

    def has_seat_area(self):
        elements = self.driver.find_elements(*self.SEAT_AREA_INPUTS)
        return len(elements) > 0
