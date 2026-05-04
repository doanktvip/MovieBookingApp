from movieapp.test.pages.AdminPage import AdminPage


def test_normal_user_cannot_access_admin(logged_in_driver):
    test_driver = logged_in_driver("nguyendoan", "123456")
    test_driver.get("http://127.0.0.1:5000/admin/")

    page_source = test_driver.page_source
    assert "403" in page_source or "Forbidden" in page_source


def test_admin_dashboard_access(logged_in_driver):
    test_driver = logged_in_driver("admin123", "123456")
    admin_page = AdminPage(test_driver)
    admin_page.open_page()

    assert "Hệ Thống Đặt Vé" in admin_page.get_brand_name()


def test_admin_navigate_menus(logged_in_driver):
    test_driver = logged_in_driver("admin123", "123456")
    admin_page = AdminPage(test_driver)
    admin_page.open_page()

    # Cơ sở vật chất
    admin_page.open_co_so_vat_chat_menu()
    admin_page.click_province()
    assert "/admin/province" in admin_page.get_current_url()

    # Phim và Lịch chiếu
    admin_page.open_phim_lich_chieu_menu()
    admin_page.click_movie()
    assert "/admin/movie" in admin_page.get_current_url()

    # Người dùng
    admin_page.click_user_menu()
    assert "/admin/user" in admin_page.get_current_url()
