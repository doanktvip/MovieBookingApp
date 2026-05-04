from movieapp.test.pages.HomePage import HomePage
from movieapp.test.pages.LoginPage import LoginPage


def test_login_flow_success(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")
    login_page = LoginPage(test_driver)
    assert login_page.is_user_avatar_displayed() is True


def test_login_flow_invalid_password(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()
    login_page.login("nguyendoan", "1234567")

    assert login_page.is_user_avatar_displayed() is False
