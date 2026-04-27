import time
from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.keys import Keys


class UserInfoPage(BasePage):
    URL = 'http://127.0.0.1:5000/userinfo'

    BTN_OPEN_EDIT_MODAL = (By.CSS_SELECTOR, "button[data-bs-target='#editProfileModal']")
    INPUT_EMAIL = (By.CSS_SELECTOR, "#editProfileModal input[name='email']")
    BTN_SAVE_PROFILE = (By.CSS_SELECTOR, "#editProfileModal button[type='submit']")

    # --- Locators: Modal Đổi mật khẩu ---
    BTN_OPEN_PWD_MODAL = (By.CSS_SELECTOR, "button[data-bs-target='#changePasswordModal']")
    INPUT_OLD_PWD = (By.CSS_SELECTOR, "input[name='old_password']")
    INPUT_NEW_PWD = (By.CSS_SELECTOR, "input[name='new_password']")
    INPUT_CONFIRM_PWD = (By.CSS_SELECTOR, "input[name='confirm_password']")
    BTN_SAVE_PWD = (By.CSS_SELECTOR, "#changePasswordModal button[type='submit']")

    def open_page(self):
        self.open(self.URL)

    def open_edit_profile_modal(self):
        self.js_click(*self.BTN_OPEN_EDIT_MODAL)
        time.sleep(1)

    def edit_email(self, new_email):
        self.js_typing(*self.INPUT_EMAIL, new_email)
        self.js_click(*self.BTN_SAVE_PROFILE)

    def open_change_password_modal(self):
        self.js_click(*self.BTN_OPEN_PWD_MODAL)
        time.sleep(1)

    def change_password(self, old_pwd, new_pwd, confirm_pwd):
        self.js_typing(*self.INPUT_OLD_PWD, old_pwd)
        self.js_typing(*self.INPUT_NEW_PWD, new_pwd)
        self.js_typing(*self.INPUT_CONFIRM_PWD, confirm_pwd)
        self.js_click(*self.BTN_SAVE_PWD)
