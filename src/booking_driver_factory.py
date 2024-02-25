from logging import Logger

from selenium.webdriver import Remote, Firefox
from selenium.webdriver.firefox.options import Options

from src.config import GlobalBookingConfig
from src.constants import IS_PRODUCTION


class BookingDriverFactory:

    def __init__(self, logger: Logger, config: GlobalBookingConfig):
        self._logger = logger
        self._config = config

    def get_driver(self):
        driver_options = Options()

        if self._config.headless_mode:
            self._logger.info("Headless browser")
            driver_options.add_argument("--headless")

        if not IS_PRODUCTION:
            self._logger.info("Local mode")
            return Firefox(options=driver_options)

        self._logger.info("Remote mode")
        return Remote(command_executor="http://localhost:4444", options=driver_options)
