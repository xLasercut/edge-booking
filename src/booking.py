import json
import time
from datetime import datetime, timedelta
from logging import Logger
from typing import Tuple

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.booking_driver_factory import BookingDriverFactory
from src.config import GlobalBookingConfig, UserBookingConfig
from src.constants import IS_PRODUCTION, SCREENSHOT_DIR
from src.exceptions import ApiError, ActivityNotFoundError
from src.models import (
    UserCredentials,
    ActivityDetails,
    ActivitySubLocationDetails,
)


class Booking:
    def __init__(
        self,
        logger: Logger,
        global_config: GlobalBookingConfig,
        user_config: UserBookingConfig,
    ):
        driver_factory = BookingDriverFactory(logger, global_config)
        self._logger = logger
        self._browser = driver_factory.get_driver()
        self._global_config = global_config
        self._user_config = user_config

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

    def _click_cookie_button(self):
        cookie_button = self._wait_element_exists((By.TAG_NAME, "button"))
        while cookie_button.text != "Accept":
            cookie_button = self._browser.find_element(By.TAG_NAME, "button")
        cookie_button.click()

    def _login(self):
        username_input = self._wait_element_exists((By.ID, "xn-Username"))
        password_input = self._wait_element_exists((By.ID, "xn-Password"))
        login_button = self._wait_element_exists((By.ID, "login"))
        username_input.send_keys(self._user_config.username)
        password_input.send_keys(self._user_config.password)
        login_button.click()

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

    def _fill_payment_details(self):
        self._logger.info("filling in address")
        address_button = self._wait_element_exists(
            (By.XPATH, '//a[text()="Enter your address manually"]')
        )
        address_button.click()
        self._browser.find_element(
            By.XPATH,
            '//select[@id="oCustomer-sCountryCode"]/option[text()="United Kingdom"]',
        ).click()
        self._browser.find_element(By.ID, "oCustomer-sAddressLine1").send_keys(
            self._user_config.address_line_1
        )
        self._browser.find_element(By.ID, "oCustomer-sTown").send_keys(
            self._user_config.address_city
        )
        self._browser.find_element(By.ID, "oCustomer-sPostCode").send_keys(
            self._user_config.address_postcode
        )
        self._browser.find_element(By.ID, "oCustomer-sCardholderName").send_keys(
            self._user_config.payer_name
        )
        self._browser.find_element(By.ID, "oCustomer-sTelephoneNumber").send_keys(
            self._user_config.contact_number
        )
        self._browser.find_element(By.ID, "form-submit").click()
        _ = self._wait_element_exists((By.ID, "oCard-sCardHolderName"))
        self._logger.info("filling in payment details")
        self._browser.find_element(
            By.XPATH, f'//span[text()="{self._user_config.card_type}"]'
        ).click()
        self._browser.find_element(By.ID, "oCard-sCardNumber").send_keys(
            self._user_config.card_number
        )
        self._browser.find_element(By.ID, "oCard-sCVV").send_keys(
            self._user_config.card_cvv
        )
        self._browser.find_element(
            By.XPATH,
            f'//select[@id="oCard-sCardEndDateMonth"]/option[text()="{self._user_config.card_expiry_month}"]',
        ).click()
        self._browser.find_element(
            By.XPATH,
            f'//select[@id="oCard-sCardEndDateYear"]/option[text()="{self._user_config.card_expiry_year}"]',
        ).click()
        if IS_PRODUCTION:
            self._browser.find_element(By.ID, "form-submit").click()

    def _fetch_basket_id(self, access_token: str) -> str:
        self._logger.info("fetching basket id")
        request_url = "https://sportsbookings.leeds.ac.uk/LhWeb/en/api/Basket"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(url=request_url, headers=headers)
        if response.status_code != 200:
            raise ApiError(f"could not create basket: {response.text}")
        basket_id = response.text.replace('"', "")
        self._logger.info(f"created basket: {basket_id}")
        return basket_id

    def _fetch_user_credentials(self) -> UserCredentials:
        count = 0
        session_storage = self._browser.execute_script(
            'return window.localStorage.getItem("oidc.user:https://sportsbookings.leeds.ac.uk/lhweb/identity:LhWebJs")'
        )
        while not session_storage and count <= 5:
            session_storage = self._browser.execute_script(
                'return window.localStorage.getItem("oidc.user:https://sportsbookings.leeds.ac.uk/lhweb/identity:LhWebJs")'
            )
            count += 1
            time.sleep(1)

        parsed_session_storage = json.loads(session_storage)
        return UserCredentials(
            jwt=parsed_session_storage["access_token"],
            pid=parsed_session_storage["profile"]["dimension_person_pk"],
        )

    def _fetch_matching_activity(
        self, user_credentials: UserCredentials, booking_time: datetime
    ) -> ActivityDetails:
        self._logger.info("fetching matching activity")
        url = "https://sportsbookings.leeds.ac.uk/LhWeb/en/api/Sites/1/Timetables/Bookings"
        params = {
            "pid": user_credentials.pid,
            "date": f"{booking_time.strftime('%Y/%m/%d')} 00:00:00",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_credentials.jwt}",
        }
        response = requests.get(url=url, headers=headers, params=params)
        if response.status_code != 200:
            raise ApiError(f"could not fetch activities list: {response.text}")

        for item in response.json():
            activity = ActivityDetails(**item)
            self._logger.info(activity)
            if (
                activity.ActivityDescription == self._user_config.activity
                and self._user_config.start_time in activity.StartTime
            ):
                self._logger.info("found matching activity")
                return activity

        raise ActivityNotFoundError("no matching activity found")

    def _fetch_activity_sub_locations(
        self, activity: ActivityDetails, user_credentials: UserCredentials
    ) -> list[ActivitySubLocationDetails]:
        self._logger.info("fetching activity sub location...")
        url = (
            "https://sportsbookings.leeds.ac.uk/LhWeb/en/api/Bookings/SubLocationGroups"
        )
        params = {
            "siteId": "1",
            "activityCode": activity.ActivityCode,
            "locationCode": activity.LocationCode,
            "startDateTime": activity.query_start_time(),
            "endDateTime": activity.query_end_time(),
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_credentials.jwt}",
        }
        response = requests.get(url=url, headers=headers, params=params)
        if response.status_code != 200:
            raise ApiError(f"could not fetch activity sub locations: {response.text}")

        return [ActivitySubLocationDetails(**item) for item in response.json()]

    def _add_to_basket(
        self,
        activity: ActivityDetails,
        sub_locations: list[ActivitySubLocationDetails],
        user_credentials: UserCredentials,
    ) -> str:
        count = 0
        self._logger.info("adding activity to basket")
        basket_id = self._fetch_basket_id(user_credentials.jwt)
        url = (
            f"https://sportsbookings.leeds.ac.uk/LhWeb/en/api/Basket/{basket_id}/Items"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_credentials.jwt}",
        }
        while count <= self._global_config.retry_count:
            for sub_location in sub_locations:
                self._logger.info(sub_location)
                if not sub_location.Available:
                    continue

                body = {
                    "Id": 0,
                    "BasketId": basket_id,
                    "Description": activity.ActivityDescription,
                    "UntranslatedDescription": None,
                    "IncomeKey": None,
                    "IncomeCode": None,
                    "GrossAmount": 0,
                    "VATCode": "S",
                    "VATAmount": 0,
                    "Type": "Xn.Booking",
                    "DisplayOrder": 1,
                    "SiteId": 1,
                    "BasketItemMetadata": {
                        "ActivityCode": activity.ActivityCode,
                        "LocationCode": activity.LocationCode,
                        "LocationTypeSingular": activity.AvailablePlaceLocationDescription,
                        "ActivityGroupId": activity.ActivityGroupId,
                        "SubLocationGroup": sub_location.SubLocationGroupId,
                        "SubLocationDescription": sub_location.SubLocationNames,
                        "LocationDescription": activity.LocationDescription,
                        "StartTime": activity.StartTime,
                        "EndTime": activity.EndTime,
                        "SiteName": "Sport & Physical Activity",
                    },
                    "DurationDescription": None,
                    "FormattedGrossAmount": None,
                    "Quantity": 0,
                    "ItemOwnerPersonFK": user_credentials.pid,
                }
                self._logger.info(body)
                response = requests.post(
                    url=url, headers=headers, data=json.dumps(body)
                )
                if response.status_code == 200:
                    return basket_id

                self._logger.info(response.text)
            time.sleep(1)
            count += 1
        raise ApiError("could not add to basket")

    def _go_to_checkout(self, basket_id: str):
        self._browser.get(
            f"https://sportsbookings.leeds.ac.uk/LhWeb/en/Members/Home/BasketDetails?basketId={basket_id}"
        )

    def start(self):
        try:
            self._logger.info("starting booking...")
            self._browser.get("https://sportsbookings.leeds.ac.uk/lhweb/identity/login")
            self._click_cookie_button()
            self._login()
            user_credentials = self._fetch_user_credentials()
            current_time = datetime.now()
            self._logger.info(f"current time: {current_time.isoformat()}")
            booking_time = current_time + timedelta(days=self._global_config.day_delta)
            self._logger.info(f"booking time: {booking_time.isoformat()}")
            activity = self._fetch_matching_activity(user_credentials, booking_time)
            sub_locations = self._fetch_activity_sub_locations(
                activity, user_credentials
            )
            basket_id = self._add_to_basket(activity, sub_locations, user_credentials)
            self._go_to_checkout(basket_id)
            self._confirm_checkout()
            self._fill_payment_details()
            time.sleep(20)
            self._browser.get_screenshot_as_file(str(SCREENSHOT_DIR / f"{current_time.isoformat()}.png"))
            self._browser.quit()
            self._logger.info("booking ended")
        except Exception as e:
            self._logger.error("could not book activity")
            self._logger.exception(e)
            self._browser.quit()
