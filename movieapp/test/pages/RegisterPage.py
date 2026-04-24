from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    TAB_REGISTER = (By.ID, "tab-register")

    USERNAME_FIELD = (By.ID, "username1")
    EMAIL_FIELD = (By.ID, "email")
    PASSWORD_FIELD = (By.ID, "password1")
    CONFIRM_PASSWORD_FIELD = (By.ID, "confirm_password")
    BUTTON_SUBMIT = (By.CSS_SELECTOR, "button[onclick*='handleRegister']")

    def open_register_tab(self):
        self.click(*self.TAB_REGISTER)

    def register(self, username, email, password, confirm_password):
        self.typing(*self.USERNAME_FIELD, username)
        self.typing(*self.EMAIL_FIELD, email)
        self.typing(*self.PASSWORD_FIELD, password)
        self.typing(*self.CONFIRM_PASSWORD_FIELD, confirm_password)
        self.click(*self.BUTTON_SUBMIT)
