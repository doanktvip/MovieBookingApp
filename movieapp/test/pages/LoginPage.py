from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/'

    BUTTON_MODAL_LOGIN = (By.CSS_SELECTOR, '[data-bs-target="#authModal"]')
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    TAB_LOGIN = (By.ID, "tab-login")
    BUTTON_LOGIN = (By.CSS_SELECTOR, "button[onclick*='handleLogin']")
    MODAL_CONTAINER = (By.ID, "authModal")

    def open_page(self):
        self.open(self.URL)

    def open_login_modal(self):
        self.js_click(*self.BUTTON_MODAL_LOGIN)

    def open_login_tab(self):
        self.js_click(*self.TAB_LOGIN)

    def login(self, username, password, expect_success=True):
        self.js_typing(*self.USERNAME, username)
        self.js_typing(*self.PASSWORD, password)
        self.js_click(*self.BUTTON_LOGIN)
        if expect_success:
            self.wait.until(EC.invisibility_of_element_located(self.MODAL_CONTAINER))
