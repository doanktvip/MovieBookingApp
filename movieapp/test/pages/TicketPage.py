from selenium.webdriver.common.by import By
from movieapp.test.pages.BasePage import BasePage


class TicketPage(BasePage):
    URL = 'http://127.0.0.1:5000/tickets'

    def open_page(self):
        self.open(self.URL)

    def get_booking_card_by_seats(self, seat_names):
        expected_seats_str = ", ".join(seat_names)

        cards = self.finds(By.CSS_SELECTOR, ".col-12.mb-4")

        for card in cards:
            try:
                p_tags = card.find_elements(By.TAG_NAME, "p")
                seats_text = ""

                for p in p_tags:
                    if "Ghế:" in p.text:
                        seats_text = p.find_element(By.TAG_NAME, "strong").text.strip()
                        break

                if seats_text == expected_seats_str:
                    return card
            except:
                continue

        return None

    def click_pay_again_for_seats(self, seat_names):
        card = self.get_booking_card_by_seats(seat_names)
        if card:
            btn = card.find_element(By.CSS_SELECTOR, "button.btn-outline-success")
            btn.click()
            return True
        return False

    def click_cancel_for_seats(self, seat_names):
        card = self.get_booking_card_by_seats(seat_names)
        if card:
            btn = card.find_element(By.CSS_SELECTOR, "button.btn-outline-danger")
            modal_target_id = btn.get_attribute("data-bs-target")
            btn.click()
            return modal_target_id
        return None

    def get_status_badge_text(self, seat_names):
        card = self.get_booking_card_by_seats(seat_names)
        return card.find_element(By.CSS_SELECTOR, ".badge").text.strip()

    def confirm_cancel(self, modal_target_id):
        confirm_btn_selector = f"{modal_target_id} button[type='submit'].btn-danger"
        self.click(By.CSS_SELECTOR, confirm_btn_selector)

    def get_alert_message(self):
        return self.get_text(By.CSS_SELECTOR, ".alert-success, .alert-danger")
