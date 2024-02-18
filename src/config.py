from configparser import ConfigParser

from src.constants import CONFIG_FILE_PATH


class BookingConfig:
    def __init__(self):
        self._config_parser = ConfigParser()
        self._config_parser.read(CONFIG_FILE_PATH)
        if not self._config_parser.has_section("config"):
            raise Exception("Invalid config file")

    def _config(self):
        return self._config_parser["config"]

    def username(self) -> str:
        return self._config()["username"]

    def password(self) -> str:
        return self._config()["password"]

    def booking_url(self) -> str:
        return self._config()["booking_url"]

    def headless(self) -> bool:
        return self._config()["headless"].lower() == "true"
