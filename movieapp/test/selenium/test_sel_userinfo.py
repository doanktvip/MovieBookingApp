import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.UserInfoPage import UserInfoPage


def login_helper(driver, password="123456"):
    login_page = LoginPage(driver)
    login_page.open("http://127.0.0.1:5000/")
    time.sleep(1)
    login_page.open_login_modal()
    time.sleep(1)
    login_page.open_login_tab()
    login_page.login("nguyendoan", password)
    time.sleep(1)


def test_view_user_info(driver):
    login_helper(driver)

    userinfo_page = UserInfoPage(driver)
    userinfo_page.open_page()
    time.sleep(1)
    username_display = driver.find_element(By.CSS_SELECTOR, "h3.fw-bold.mb-1")
    assert "nguyendoan" in username_display.text
    email_display = driver.find_element(By.CSS_SELECTOR, "p.text-secondary.mb-4.fs-5")
    assert "@" in email_display.text


def test_edit_email(driver):
    login_helper(driver)
    userinfo_page = UserInfoPage(driver)
    userinfo_page.open_page()
    time.sleep(1)

    new_test_email = f"email{uuid.uuid4().hex[:5]}@gmail.com"
    userinfo_page.open_edit_profile_modal()
    userinfo_page.edit_email(new_test_email)
    wait = WebDriverWait(driver, 10)
    is_email_updated = wait.until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "p.text-secondary.mb-4.fs-5"), new_test_email))
    assert is_email_updated is True
    email_display = driver.find_element(By.CSS_SELECTOR, "p.text-secondary.mb-4.fs-5")
    assert new_test_email in email_display.text


def test_change_password(driver):
    login_helper(driver)
    userinfo_page = UserInfoPage(driver)
    userinfo_page.open_page()
    time.sleep(1)

    NEW_PWD = "newpassword123"
    userinfo_page.open_change_password_modal()
    userinfo_page.change_password(old_pwd="123456", new_pwd=NEW_PWD, confirm_pwd=NEW_PWD)
    time.sleep(2)

    driver.get("http://127.0.0.1:5000/logout")
    time.sleep(1)

    login_helper(driver, NEW_PWD)

    userinfo_page.open_page()
    time.sleep(1)
    username_display = driver.find_element(By.CSS_SELECTOR, "h3.fw-bold.mb-1")
    assert "nguyendoan" in username_display.text

    userinfo_page.open_change_password_modal()
    userinfo_page.change_password(old_pwd=NEW_PWD, new_pwd="123456", confirm_pwd="123456")
    username_display = driver.find_element(By.CSS_SELECTOR, "h3.fw-bold.mb-1")
    assert "nguyendoan" in username_display.text
