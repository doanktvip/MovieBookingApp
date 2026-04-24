import time
import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from movieapp.test.pages.HomePage import HomePage
from movieapp.test.pages.LoginPage import LoginPage


def test_login_flow_success(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()
    time.sleep(1)

    login_page.login("admin123", "123456")
    time.sleep(1)

    user_avatar = driver.find_element(By.CSS_SELECTOR, ".dropdown img.rounded-circle").is_displayed()
    assert user_avatar is True


def test_login_flow_invalid_password(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()
    time.sleep(1)

    login_page.login("admin123", "sai_mat_khau_ne")
    time.sleep(1)

    with pytest.raises(NoSuchElementException):
        driver.find_element(By.CSS_SELECTOR, ".dropdown img.rounded-circle")
