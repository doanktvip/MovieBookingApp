from movieapp.test.pages.MovieDetailPage import MovieDetailPage


def test_view_random_movie_detail_and_showtimes(driver):
    movie_detail_page = MovieDetailPage(driver)
    movie_title_random = movie_detail_page.select_random_valid_movie_and_showtime(click_showtime=False)

    assert "/movies/" in movie_detail_page.get_current_url()
    assert movie_detail_page.get_movie_title() == movie_title_random
    assert movie_detail_page.is_showtime_tab_active()
    assert movie_detail_page.is_showtime_container_displayed()
