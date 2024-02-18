import time

import schedule
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from src.booking import Booking
from src.config import BookingConfig


def booking_job():
    booking_config = BookingConfig()
    driver_options = Options()
    if booking_config.headless():
        driver_options.add_argument('--headless')
    browser = Firefox(options=driver_options)
    booking = Booking(browser, booking_config)
    booking.start()


if __name__ == '__main__':
    schedule.every(30).minutes.do(booking_job)
    while True:
        schedule.run_pending()
        time.sleep(1)
