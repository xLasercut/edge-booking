import os


class BookingConfig:

    @staticmethod
    def username() -> str:
        return os.environ["BOOKING_USERNAME"]

    @staticmethod
    def password() -> str:
        return os.environ["BOOKING_PASSWORD"]

    @staticmethod
    def booking_url() -> str:
        return os.environ["BOOKING_URL"]

    @staticmethod
    def headless() -> bool:
        return os.environ["BOOKING_HEADLESS_MODE"].lower() == "true"
