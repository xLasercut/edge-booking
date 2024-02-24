from configparser import ConfigParser

from src.constants import CONFIG_DIR, CONFIG_GLOBAL_SECTION


class BookingConfig:
    def __init__(self):
        self._parser = ConfigParser()
        self._parser.read(str(CONFIG_DIR / "config.ini"))

    def accounts(self):
        return [
            section
            for section in self._parser.sections()
            if section != CONFIG_GLOBAL_SECTION
        ]

    def username(self, account: str) -> str:
        return self._parser[account]["username"]

    def password(self, account: str) -> str:
        return self._parser[account]["password"]

    def headless(self) -> bool:
        return self._parser[CONFIG_GLOBAL_SECTION]["headless_mode"].lower() == "true"

    def local(self) -> bool:
        return self._parser[CONFIG_GLOBAL_SECTION]["local_mode"].lower() == "true"

    def start_time(self) -> str:
        return self._parser[CONFIG_GLOBAL_SECTION]["start_time"]

    def day_delta(self) -> int:
        return int(self._parser[CONFIG_GLOBAL_SECTION]["day_delta"])

    def address_line_1(self, account: str) -> str:
        return self._parser[account]["address_line_1"]

    def address_city(self, account: str) -> str:
        return self._parser[account]["address_city"]

    def address_postcode(self, account: str) -> str:
        return self._parser[account]["address_postcode"]

    def payer_name(self, account: str) -> str:
        return self._parser[account]["payer_name"]

    def contact_number(self, account: str) -> str:
        return self._parser[account]["contact_number"]
