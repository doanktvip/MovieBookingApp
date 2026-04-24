import time
import pytest
import uuid
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from movieapp.test.pages.HomePage import HomePage
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.RegisterPage import RegisterPage


def test_register_flow_success(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()
    time.sleep(1)
    register_page = RegisterPage(driver)
    register_page.open_register_tab()
    time.sleep(1)

    unique_user = f"user_{uuid.uuid4().hex[:5]}"

    register_page.register(unique_user, f"{unique_user}@gmail.com", "123456", "123456")
    time.sleep(2)
    login_page.login(unique_user, "123456")
    time.sleep(1)
    user_avatar = driver.find_element(By.CSS_SELECTOR, ".dropdown img.rounded-circle").is_displayed()
    assert user_avatar is True


def test_register_fail_password_mismatch(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()
    time.sleep(1)
    register_page = RegisterPage(driver)
    register_page.open_register_tab()
    time.sleep(1)

    unique_user = f"user_{uuid.uuid4().hex[:5]}"

    register_page.register(unique_user, f"{unique_user}@gmail.com", "123456", "1")
    time.sleep(1)
    login_page.open_login_tab()
    time.sleep(1)
    login_page.login(unique_user, "123456")
    time.sleep(1)
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.CSS_SELECTOR, ".dropdown img.rounded-circle")
