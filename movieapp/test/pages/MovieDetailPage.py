import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from movieapp.test.pages.BasePage import BasePage


class MovieDetailPage(BasePage):
    URL = 'http://127.0.0.1:5000/movies'
    SHOWTIME_LINKS = (By.CSS_SELECTOR, '#showtime-container a')
    ALL_MOVIE_LINKS = (By.CSS_SELECTOR, '#movie-container > div.row.g-4 > div > a')
    MOVIE_TITLE = (By.CSS_SELECTOR, 'h1.movie-title')
    SHOWTIME_TAB = (By.ID, 'pills-showtime-tab')
    SHOWTIME_CONTAINER = (By.ID, 'showtime-container')

    def open_page(self):
        self.open(self.URL)

    def get_movie_title(self):
        return self.get_text(*self.MOVIE_TITLE)

    def is_showtime_tab_active(self):
        tab = self.find(*self.SHOWTIME_TAB)
        return "active" in tab.get_attribute("class")

    def is_showtime_container_displayed(self):
        return self.is_displayed(*self.SHOWTIME_CONTAINER)

    def select_random_valid_movie_and_showtime(self, click_showtime=True):
        while True:
            self.open_page()
            elements = self.finds(*self.ALL_MOVIE_LINKS)
            if not elements:
                continue  # pragma: no cover

            selected_index = random.randint(0, len(elements) - 1)
            movie_el = elements[selected_index]
            full_card_text = movie_el.text.strip()
            title_only = full_card_text.split('\n')[1] if '\n' in full_card_text else full_card_text

            self.driver.execute_script("arguments[0].click();", movie_el)

            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='date']")))
            except:  # pragma: no cover
                continue

            date_inputs = self.finds(By.CSS_SELECTOR, "input[name='date']")
            date_values = [d.get_attribute("value") for d in date_inputs]
            if not date_values:
                continue  # pragma: no cover

            random.shuffle(date_values)
            valid_st = False
            for dv in date_values:
                try:
                    d_input = self.find(By.CSS_SELECTOR, f"input[name='date'][value='{dv}']")
                    d_id = d_input.get_attribute('id')
                    label = self.find(By.CSS_SELECTOR, f"label[for='{d_id}']")
                    self.driver.execute_script("arguments[0].click();", label)

                    self.wait.until(EC.staleness_of(d_input))
                    self.wait.until(EC.presence_of_element_located((By.ID, "showtime-container")))
                except:  # pragma: no cover
                    pass  # pragma: no cover

                try:
                    all_sts = self.driver.find_elements(*self.SHOWTIME_LINKS)

                    valid_sts = []
                    for st in all_sts:
                        href = st.get_attribute("href") or ""
                        onclick = st.get_attribute("onclick") or ""
                        css_class = st.get_attribute("class") or ""

                        is_logged_in_link = "/booking/showtime" in href
                        is_logged_out_link = "/booking/showtime" in onclick
                        is_not_disabled = "disabled" not in css_class

                        if (is_logged_in_link or is_logged_out_link) and is_not_disabled:
                            valid_sts.append(st)

                    if valid_sts:
                        if click_showtime:
                            st = random.choice(valid_sts)
                            self.driver.execute_script("arguments[0].click();", st)
                        valid_st = True
                        break
                except:  # pragma: no cover
                    pass

            if valid_st:
                return title_only
