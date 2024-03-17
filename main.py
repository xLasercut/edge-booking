import logging
import time
from datetime import datetime

import schedule

from src.booking import Booking
from src.config import BookingConfigFactory
from src.constants import LOG_DIR


def booking_job(config_factory: BookingConfigFactory) -> None:
    current_time = datetime.now()
    logger_format = "%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s"
    formatter = logging.Formatter(logger_format)
    logging.basicConfig(format=logger_format)
    logger = logging.getLogger(f"selenium - {current_time.isoformat()}")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(
        filename=str(LOG_DIR / f"{current_time.isoformat()}.log")
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    global_config = config_factory.get_global_config()

    for account in config_factory.accounts():
        user_config = config_factory.get_user_config(account)
        booking = Booking(logger, global_config, user_config)
        booking.start()


if __name__ == "__main__":
    booking_config_factory = BookingConfigFactory()
    if booking_config_factory.get_global_config().scheduled:
        schedule.every().day.at("06:00").do(
            booking_job, config_factory=booking_config_factory
        )
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        booking_job(booking_config_factory)
