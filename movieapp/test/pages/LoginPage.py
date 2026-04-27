from selenium.webdriver.common.by import By

from movieapp.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    BUTTON_MODAL_LOGIN = (By.CSS_SELECTOR, '[data-bs-target="#authModal"]')
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    TAB_LOGIN = (By.ID, "tab-login")
    BUTTON_LOGIN = (By.CSS_SELECTOR, "button[onclick*='handleLogin']")

    def open_login_modal(self):
        self.js_click(*self.BUTTON_MODAL_LOGIN)

    def open_login_tab(self):
        self.js_click(*self.TAB_LOGIN)

    def login(self, username, password):
        self.js_typing(*self.USERNAME, username)
        self.js_typing(*self.PASSWORD, password)
        self.js_click(*self.BUTTON_LOGIN)
