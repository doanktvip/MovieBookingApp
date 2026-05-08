from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CheckoutPage(BasePage):
    MOMO_RADIO = (By.CSS_SELECTOR, "input[value='momo']")
    PAY_BUTTON = (By.CSS_SELECTOR, "button[type='submit'].btn-danger")

    def select_momo(self):
        self.js_click(*self.MOMO_RADIO)

    def click_pay_button(self):
        self.js_click(*self.PAY_BUTTON)

    def is_on_page(self):
        WebDriverWait(self.driver, 10).until(EC.url_contains("/checkout"))
        return True
