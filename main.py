import logging
import time
from datetime import datetime

import schedule

from src.booking import Booking
from src.config import BookingConfigFactory
from src.constants import LOG_DIR, IS_PRODUCTION


def booking_job():
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
    config_factory = BookingConfigFactory()
    global_config = config_factory.get_global_config()

    for account in config_factory.accounts():
        user_config = config_factory.get_user_config(account)
        booking = Booking(logger, global_config, user_config)
        booking.start()


if __name__ == "__main__":
    if IS_PRODUCTION:
        schedule.every().day.at("05:50").do(booking_job)
        schedule.every().day.at("06:00").do(booking_job)
        schedule.every().day.at("06:10").do(booking_job)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        booking_job()
