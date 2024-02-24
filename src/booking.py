import time
from datetime import datetime, timedelta
from logging import Logger
from typing import Tuple

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.booking_driver_factory import BookingDriverFactory
from src.config import BookingConfig
from src.models import BookingCardDetails


class Booking:
    def __init__(self, logger: Logger, config: BookingConfig):
        driver_factory = BookingDriverFactory(logger, config)
        self._logger = logger
        self._browser = driver_factory.get_driver()
        self._config = config

    def _wait_element_exists(
        self, locator: Tuple[str, str], duration: int = 10, driver=None
    ):
        if driver is not None:
            return WebDriverWait(driver, duration).until(
                EC.presence_of_element_located(locator)
            )
        return WebDriverWait(self._browser, duration).until(
            EC.presence_of_element_located(locator)
        )

    def _wait_element_not_exists(self, locator: Tuple[str, str], duration: int = 10):
        return WebDriverWait(self._browser, duration).until(
            EC.invisibility_of_element_located(locator)
        )

    def _click_cookie_button(self):
        cookie_button = self._wait_element_exists((By.TAG_NAME, "button"))
        while cookie_button.text != "Accept":
            cookie_button = self._browser.find_element(By.TAG_NAME, "button")
        cookie_button.click()

    def _login(self, account: str):
        username_input = self._wait_element_exists((By.ID, "xn-Username"))
        password_input = self._wait_element_exists((By.ID, "xn-Password"))
        login_button = self._wait_element_exists((By.ID, "login"))
        username_input.send_keys(self._config.username(account))
        password_input.send_keys(self._config.password(account))
        login_button.click()

    def _go_to_online_booking(self):
        self._wait_element_exists((By.ID, "xn-online-booking-link")).click()

    def _get_booking_month_and_year(self) -> datetime:
        month_label = self._wait_element_exists((By.CLASS_NAME, "month-name"))
        return datetime.strptime(month_label.text, "%B %Y")

    def _go_to_booking_date(self, booking_date: datetime):
        calendar_button = self._wait_element_exists(
            (By.XPATH, '//li[@aria-label="Show Calendar"]')
        )

        calendar_button.click()
        parsed_month_label = self._get_booking_month_and_year()
        while (
            parsed_month_label.month != booking_date.month
            or parsed_month_label.year != booking_date.year
        ):
            self._wait_element_exists((By.CLASS_NAME, "next-month")).click()
            parsed_month_label = self._get_booking_month_and_year()

        day_elements = self._browser.find_elements(
            By.XPATH, f'//span[text()="{booking_date.day}"]'
        )
        for day_element in day_elements:
            parent_class = day_element.find_element(By.XPATH, "..").get_attribute(
                "class"
            )
            if (
                parent_class == "calendar-day"
                or parent_class == "calendar-day selected"
            ):
                day_element.click()
                break

    @staticmethod
    def _is_badminton(booking_card) -> bool:
        badminton_images = booking_card.find_elements(
            By.XPATH, './/div[@class="xn-image xn-img-badminton"]'
        )
        return len(badminton_images) > 0

    def _validate_fully_booked(self):
        fully_booked = self._browser.find_elements(
            By.XPATH, '//div[text()="This activity is fully booked."]'
        )
        if len(fully_booked) > 0:
            raise Exception("This activity is fully booked.")

    def _validate_in_allowed_booking_limits(self):
        outside_of_book_limit = self._browser.find_elements(
            By.XPATH,
            '//div[text()="This activity is outside of the book ahead limits allowed."]',
        )
        if len(outside_of_book_limit) > 0:
            raise Exception(
                "This activity is outside of the book ahead limits allowed."
            )

    def _validate_add_to_basket_error(self):
        count = 0
        while count <= 5:
            self._validate_fully_booked()
            self._validate_in_allowed_booking_limits()
            time.sleep(1)
            count += 1

    @staticmethod
    def _get_booking_card_details(booking_card) -> BookingCardDetails:
        booking_card_content = booking_card.find_element(
            By.XPATH, './/div[@class="xn-content"]'
        )
        return BookingCardDetails(
            location=booking_card_content.find_element(
                By.XPATH, './/div[@class="xn-booking-location"]'
            ).text,
            activity=booking_card.find_element(
                By.XPATH, './/div[@class="xn-heading"]'
            ).text,
            start_time=booking_card_content.find_element(
                By.XPATH, './/div[@class="xn-booking-starttime"]'
            ).text,
            spaces_left=booking_card_content.find_element(
                By.XPATH, './/div[@class="xn-booking-spaces"]'
            ).text,
        )

    def _add_to_basket(self):
        _ = self._wait_element_exists(
            (By.XPATH, '//div[@class="xn-booking-description"]')
        )
        booking_descriptions = self._browser.find_elements(
            By.XPATH, '//div[@class="xn-booking-description"]'
        )
        for booking_description in booking_descriptions:
            booking_card = self._wait_element_exists(
                (By.XPATH, ".."), driver=booking_description
            )
            booking_card_details = self._get_booking_card_details(booking_card)
            self._logger.info(
                f"found booking: {booking_card_details}"
            )
            if booking_card_details.activity == "Badminton" and booking_card_details.start_time == self._config.start_time():
                booking_card.find_element(
                    By.XPATH, './/button[text()="Add to Basket"]'
                ).click()
                self._logger.info(
                    f"added to basket: {booking_card_details}"
                )
                self._validate_add_to_basket_error()

        raise Exception(
            f"did not find available slots for time: {self._config.start_time()}"
        )

    def _go_to_checkout(self):
        count = 0
        basket_item_count = self._wait_element_exists(
            (By.XPATH, '//div[@data-bind="text: itemCount"]')
        )
        while basket_item_count.text != "1":
            basket_item_count = self._wait_element_exists(
                (By.XPATH, '//div[@data-bind="text: itemCount"]')
            )
            time.sleep(1)
            count += 1
            if count > 5:
                raise Exception("failed to go to checkout")

        action_chain = ActionChains(self._browser)
        basket_button = self._browser.find_element(By.CLASS_NAME, "xn-icon")
        action_chain.move_to_element(basket_button).perform()
        checkout_button = self._browser.find_element(By.XPATH, '//a[text()="Checkout"]')
        action_chain.move_to_element(checkout_button).click().perform()
        self._logger.info("going to checkout...")

    def _confirm_checkout(self):
        pay_now_button = self._wait_element_exists(
            (By.XPATH, '//button[text()="Pay Now"]')
        )
        activity = self._browser.find_element(
            By.XPATH, '//span[@data-bind="text: Description"]'
        ).text
        start_time = self._browser.find_element(
            By.XPATH, '//span[@data-bind="text: BookingFormattedDateTime"]'
        ).text
        location = self._browser.find_element(
            By.XPATH, '//span[@data-bind="text: Location"]'
        ).text
        court = self._browser.find_element(
            By.XPATH, '//span[@data-bind="text: SubLocationName"]'
        ).text
        self._logger.info(
            f"confirming booking - activity: {activity} - location: {location} - start_time: {start_time} - court: {court}"
        )
        pay_now_button.click()
        continue_button = self._wait_element_exists(
            (By.XPATH, '//button[@id="form-submit"]')
        )

        continue_button.click()

    def _fill_payment_details(self, account: str):
        address_button = self._wait_element_exists(
            (By.XPATH, '//a[text()="Enter your address manually"]')
        )
        address_button.click()
        self._browser.find_element(
            By.XPATH,
            '//select[@id="oCustomer-sCountryCode"]/option[text()="United Kingdom"]',
        ).click()
        self._browser.find_element(By.ID, "oCustomer-sAddressLine1").send_keys(
            self._config.address_line_1(account)
        )
        self._browser.find_element(By.ID, "oCustomer-sTown").send_keys(
            self._config.address_city(account)
        )
        self._browser.find_element(By.ID, "oCustomer-sPostCode").send_keys(
            self._config.address_postcode(account)
        )
        self._browser.find_element(By.ID, "oCustomer-sCardholderName").send_keys(
            self._config.payer_name(account)
        )
        self._browser.find_element(By.ID, "oCustomer-sTelephoneNumber").send_keys(
            self._config.contact_number(account)
        )
        self._browser.find_element(By.ID, "form-submit").click()

    def start(self, account: str):
        try:
            self._logger.info("starting booking...")
            self._browser.get("https://sportsbookings.leeds.ac.uk/lhweb/identity/login")
            self._click_cookie_button()
            self._login(account)
            self._go_to_online_booking()
            current_date = datetime.now()
            self._logger.info(f"current time {current_date.isoformat()}")
            booking_date = current_date + timedelta(days=self._config.day_delta())
            self._logger.info(f"booking date: {booking_date.isoformat()}")
            self._go_to_booking_date(booking_date)
            self._add_to_basket()
            self._go_to_checkout()
            self._confirm_checkout()
            # self._fill_payment_details(account)

            self._browser.quit()
            self._logger.info("booking ended")
        except Exception as e:
            self._logger.error("could not book activity")
            self._logger.exception(e)
            self._browser.quit()
