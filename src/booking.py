import time
from datetime import datetime, timedelta

from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from src.config import BookingConfig
from src.constants import AVAILABLE_DIR
import json


class Booking:
    def __init__(self, driver: Firefox, config: BookingConfig):
        self._browser = driver
        self._day_deltas = [7, 14]
        self._booking_time = '16:00'
        self._config = config

    def _click_cookie_button(self):
        cookie_button = self._browser.find_element(By.TAG_NAME, 'button')
        while cookie_button.text != 'Accept':
            cookie_button = self._browser.find_element(By.TAG_NAME, 'button')
        cookie_button.click()

    def _login(self):
        username_input = self._browser.find_element(By.ID, 'xn-Username')
        password_input = self._browser.find_element(By.ID, 'xn-Password')
        login_button = self._browser.find_element(By.ID, 'login')
        username_input.send_keys(self._config.username())
        password_input.send_keys(self._config.password())
        login_button.click()

    def _go_to_online_booking(self):
        self._browser.find_element(By.ID, 'xn-online-booking-link').click()
        time.sleep(5)

    def _get_booking_month_and_year(self) -> datetime:
        month_label = self._browser.find_element(By.CLASS_NAME, 'month-name')
        return datetime.strptime(month_label.text, '%B %Y')

    def _go_to_booking_date(self, booking_date: datetime):
        self._browser.find_element(By.XPATH, '//li[@aria-label="Show Calendar"]').click()
        parsed_month_label = self._get_booking_month_and_year()
        while parsed_month_label.month != booking_date.month or parsed_month_label.year != booking_date.year:
            self._browser.find_element(By.CLASS_NAME, 'next-month').click()
            parsed_month_label = self._get_booking_month_and_year()

        day_elements = self._browser.find_elements(By.XPATH, f'//span[text()="{booking_date.day}"]')
        for day_element in day_elements:
            parent_class = day_element.find_element(By.XPATH, '..').get_attribute('class')
            if parent_class == 'calendar-day' or parent_class == 'calendar-day selected':
                day_element.click()
                time.sleep(5)
                break

    def _find_booking_start_time_element(self):
        elements = self._browser.find_elements(By.XPATH, '//div[@class="xn-booking-starttime"]')
        for element in elements:
            if element.text == self._booking_time:
                return element
        raise Exception(f"Could not find booking for time: {self._booking_time}")

    @staticmethod
    def _is_badminton(booking_card) -> bool:
        badminton_images = booking_card.find_elements(By.XPATH, './/div[@class="xn-image xn-img-badminton"]')
        return len(badminton_images) > 0

    def _fetch_all_badminton_times(self):
        badminton_times = []
        time.sleep(5)
        booking_card_contents = self._browser.find_elements(By.XPATH, '//div[@class="xn-content"]')
        for booking_card_content in booking_card_contents:
            booking_card = booking_card_content.find_element(By.XPATH, '..')
            if self._is_badminton(booking_card):
                location = booking_card_content.find_element(By.XPATH, './/div[@class="xn-booking-location"]').text
                start_time = booking_card_content.find_element(By.XPATH, './/div[@class="xn-booking-starttime"]').text
                spaces_left = booking_card_content.find_element(By.XPATH, './/div[@class="xn-booking-spaces"]').text
                badminton_times.append({
                    "location": location,
                    "start_time": start_time,
                    "spaces_left": spaces_left
                })
        return badminton_times

    def _add_to_basket(self):
        element = self._find_booking_start_time_element()
        booking_card = element.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
        booking_card.find_element(By.XPATH, './/button[text()="Add to Basket"]').click()

    def _go_to_checkout(self):
        action_chain = ActionChains(self._browser)
        basket_button = self._browser.find_element(By.CLASS_NAME, 'xn-icon')
        action_chain.move_to_element(basket_button).perform()
        checkout_button = self._browser.find_element(By.XPATH, '//a[text()="Checkout"]')
        action_chain.move_to_element(checkout_button).click().perform()

    def start(self):
        self._browser.get(self._config.booking_url())
        self._click_cookie_button()
        self._login()
        self._go_to_online_booking()
        current_date = datetime.now()
        output = []
        for day_delta in self._day_deltas:
            booking_date = current_date + timedelta(days=day_delta)
            self._go_to_booking_date(booking_date)
            badminton_times = self._fetch_all_badminton_times()
            output.append({
                "booking_date": booking_date.strftime("%Y-%m-%d"),
                "badminton_times": badminton_times
            })
        with open(AVAILABLE_DIR / f"{current_date.isoformat()}.json", "w") as f:
            f.write(json.dumps(output, indent=2))
        # self._add_to_basket()
        # self._go_to_checkout()

        self._browser.quit()
