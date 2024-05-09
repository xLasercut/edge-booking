import os
from logging import Logger

from selenium.webdriver import Remote, Firefox
from selenium.webdriver.firefox.options import Options

from src.config import GlobalBookingConfig
from src.constants import Drivers


class BookingDriverFactory:

    def __init__(self, logger: Logger, config: GlobalBookingConfig):
        self._logger = logger
        self._config = config

    def get_driver(self):
        driver_options = Options()

        if self._config.headless_mode:
            self._logger.info("Headless browser")
            driver_options.add_argument("--headless")

        if self._config.driver == Drivers.LOCAL:
            return Firefox(options=driver_options)

        if self._config.driver == Drivers.REMOTE:
            return Remote(
                command_executor=self._config.driver_url,
                options=driver_options,
            )

        raise Exception("Unknown driver")
