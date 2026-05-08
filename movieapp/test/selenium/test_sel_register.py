import uuid
from movieapp.test.pages.HomePage import HomePage
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.RegisterPage import RegisterPage


def test_register_flow_success(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()

    register_page = RegisterPage(driver)
    register_page.open_register_tab()

    unique_user = f"user_{uuid.uuid4().hex[:5]}"
    register_page.register(unique_user, f"{unique_user}@gmail.com", "123456", "123456")

    login_page.open_login_tab()
    login_page.login(unique_user, "123456")

    assert login_page.is_user_avatar_displayed() is True


def test_register_fail_password_mismatch(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    login_page = LoginPage(driver)
    login_page.open_login_modal()

    register_page = RegisterPage(driver)
    register_page.open_register_tab()

    unique_user = f"user_{uuid.uuid4().hex[:5]}"
    register_page.register(unique_user, f"{unique_user}@gmail.com", "123456", "1")

    login_page.open_login_tab()
    login_page.login(unique_user, "123456", False)

    assert login_page.is_user_avatar_displayed() is False
