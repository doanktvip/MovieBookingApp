from movieapp.test.pages.HomePage import HomePage


def test_homepage_load(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    assert "Trang chủ" in driver.title


def test_hero_carousel_slide(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    first_movie_title = home_page.get_active_hero_movie_title()
    home_page.click_next_hero_slide()
    home_page.wait_for_slide_change(first_movie_title)
    second_movie_title = home_page.get_active_hero_movie_title()

    assert first_movie_title != second_movie_title


def test_kham_pha_ngay_button_redirects_to_movies(driver):
    home_page = HomePage(driver)
    home_page.open_page()

    home_page.click_kham_pha_ngay()

    assert "/movies" in home_page.get_current_url()
