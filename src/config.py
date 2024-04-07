from configparser import ConfigParser
from typing import Literal

from pydantic import BaseModel

from src.constants import CONFIG_DIR, CONFIG_GLOBAL_SECTION
import os


class GlobalBookingConfig(BaseModel):
    headless_mode: bool
    day_delta: int
    retry_count: int
    driver: Literal["local", "remote", "docker"]
    dry_run: bool
    scheduled: bool
    schedule_time: str


class UserBookingConfig(BaseModel):
    username: str
    password: str
    activity: str
    start_time: str
    address_line_1: str
    address_city: str
    address_postcode: str
    payer_name: str
    contact_number: str
    card_type: str
    card_number: str
    card_cvv: str
    card_expiry_month: str
    card_expiry_year: str


class BookingConfigFactory:
    def __init__(self):
        self._parser = ConfigParser()
        if os.path.isfile("/run/secrets/booking_config"):
            self._parser.read("/run/secrets/booking_config")
        else:
            self._parser.read(str(CONFIG_DIR / "config.ini"))

    def get_global_config(self) -> GlobalBookingConfig:
        return GlobalBookingConfig(**self._parser[CONFIG_GLOBAL_SECTION])

    def get_user_config(self, account: str) -> UserBookingConfig:
        return UserBookingConfig(**self._parser[account])

    def accounts(self):
        return [
            section
            for section in self._parser.sections()
            if section != CONFIG_GLOBAL_SECTION
        ]
