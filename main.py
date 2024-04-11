import logging
import time
from datetime import datetime

import schedule

from src.booking import Booking
from src.config import BookingConfig
from src.constants import LOG_DIR


def booking_job(booking_config: BookingConfig) -> None:
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
    global_config = booking_config.get_global_config()

    for account in booking_config.accounts():
        user_config = booking_config.get_user_config(account)
        booking = Booking(logger, global_config, user_config)
        booking.start()


if __name__ == "__main__":
    config = BookingConfig()
    if config.get_global_config().scheduled:
        schedule.every().day.at(
            config.get_global_config().schedule_time, "Europe/London"
        ).do(booking_job, booking_config=config)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        booking_job(config)
