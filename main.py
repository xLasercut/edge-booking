import logging
from datetime import datetime

from src.booking import Booking
from src.config import BookingConfig
from src.constants import LOG_DIR
import time
import schedule


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
    booking_config = BookingConfig()
    booking = Booking(logger, booking_config)
    for account in booking_config.accounts():
        booking.start(account)


if __name__ == "__main__":
    # booking_job()
    schedule.every().day.at("05:50").do(booking_job)
    schedule.every().day.at("06:00").do(booking_job)
    schedule.every().day.at("06:10").do(booking_job)
    while True:
        schedule.run_pending()
        time.sleep(1)
