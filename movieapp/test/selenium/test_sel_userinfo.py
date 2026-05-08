import uuid
from selenium.webdriver.support.ui import WebDriverWait
from movieapp.test.pages.UserInfoPage import UserInfoPage


def test_view_user_info(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")
    userinfo_page = UserInfoPage(test_driver)
    userinfo_page.open_page()

    assert "nguyendoan" in userinfo_page.get_username_display()
    assert "@" in userinfo_page.get_email_display()


def test_edit_email(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")
    userinfo_page = UserInfoPage(test_driver)
    userinfo_page.open_page()

    new_test_email = f"email{uuid.uuid4().hex[:5]}@gmail.com"
    userinfo_page.open_edit_profile_modal()
    userinfo_page.edit_email(new_test_email)

    wait = WebDriverWait(test_driver, 10)
    wait.until(lambda d: new_test_email in userinfo_page.get_email_display())

    assert new_test_email in userinfo_page.get_email_display()


def test_change_password(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")
    userinfo_page = UserInfoPage(test_driver)
    userinfo_page.open_page()

    new_pwd = "newpassword123"

    userinfo_page.open_change_password_modal()
    userinfo_page.change_password(old_pwd="123456", new_pwd=new_pwd, confirm_pwd=new_pwd)

    wait = WebDriverWait(test_driver, 10)
    wait.until(lambda d: userinfo_page.get_current_url() == "http://127.0.0.1:5000/userinfo")

    test_driver.get("http://127.0.0.1:5000/logout")

    logged_in_driver("nguyendoan", new_pwd)
    userinfo_page.open_page()
    assert "nguyendoan" in userinfo_page.get_username_display()
    userinfo_page.open_change_password_modal()
    userinfo_page.change_password(old_pwd=new_pwd, new_pwd="123456", confirm_pwd="123456")
