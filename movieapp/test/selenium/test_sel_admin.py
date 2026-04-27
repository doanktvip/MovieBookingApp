import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.LoginPage import LoginPage
from movieapp.test.pages.AdminPage import AdminPage


def login_helper(driver, username, password="123456"):
    driver.maximize_window()

    login_page = LoginPage(driver)
    login_page.open("http://127.0.0.1:5000/")
    wait = WebDriverWait(driver, 10)

    wait.until(EC.element_to_be_clickable(LoginPage.BUTTON_MODAL_LOGIN))
    login_page.open_login_modal()
    wait.until(EC.element_to_be_clickable(LoginPage.TAB_LOGIN))
    login_page.open_login_tab()
    wait.until(EC.element_to_be_clickable(LoginPage.USERNAME))

    login_page.login(username, password)
    time.sleep(2)


def test_normal_user_cannot_access_admin(driver):
    login_helper(driver, "nguyendoan")
    driver.get("http://127.0.0.1:5000/admin/")
    time.sleep(1)

    page_source = driver.page_source
    assert "403" in page_source or "Forbidden" in page_source


def test_admin_dashboard_access(driver):
    login_helper(driver, "admin123")
    admin_page = AdminPage(driver)
    admin_page.open_page()

    wait = WebDriverWait(driver, 10)
    brand = wait.until(EC.presence_of_element_located(AdminPage.BRAND_NAME))
    assert "Hệ Thống Đặt Vé" in brand.text


def test_admin_navigate_menus(driver):
    login_helper(driver, "admin123")
    admin_page = AdminPage(driver)
    admin_page.open_page()
    wait = WebDriverWait(driver, 10)

    # Cơ sở vật chất
    wait.until(EC.element_to_be_clickable(AdminPage.MENU_CO_SO_VAT_CHAT))
    admin_page.open_co_so_vat_chat_menu()

    wait.until(EC.presence_of_element_located(AdminPage.SUBMENU_PROVINCE))
    admin_page.click_province()

    wait.until(EC.url_contains("/admin/province"))
    assert "/admin/province" in driver.current_url

    # Phim và Lịch chiếu
    wait.until(EC.element_to_be_clickable(AdminPage.MENU_PHIM_LICH_CHIEU))
    admin_page.open_phim_lich_chieu_menu()

    wait.until(EC.presence_of_element_located(AdminPage.SUBMENU_MOVIE))
    admin_page.click_movie()

    wait.until(EC.url_contains("/admin/movie"))
    assert "/admin/movie" in driver.current_url

    # Người dùng
    wait.until(EC.element_to_be_clickable(AdminPage.MENU_USER))
    admin_page.click_user_menu()

    wait.until(EC.url_contains("/admin/user"))
    assert "/admin/user" in driver.current_url