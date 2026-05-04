from movieapp.test.pages.CinemaPage import CinemaPage


def test_search_cinema(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()

    keyword = "CGV"
    cinema_page.search_cinema(keyword)

    titles = cinema_page.get_cinema_titles()
    for title in titles:
        assert keyword.lower() in title.lower()


def test_filter_cinema_by_province(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()

    province_id = "1"
    cinema_page.select_province_by_value(province_id)

    assert f"province_id={province_id}" in cinema_page.get_current_url()


def test_open_cinema_showtime_modal(driver):
    cinema_page = CinemaPage(driver)
    cinema_page.open_page()

    cinema_page.click_first_showtime_button()
    assert cinema_page.is_showtime_modal_displayed() is True
